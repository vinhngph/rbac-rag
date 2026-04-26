from sqlmodel.ext.asyncio.session import AsyncSession
from collections.abc import AsyncIterable
from functools import cached_property
from typing import List
from uuid import UUID, uuid4
from ollama import AsyncClient
from gc import collect as gc_collect
from torch.cuda import (
    is_available as cuda_is_available,
    empty_cache as cuda_empty_cache,
)
from torch.backends.mps import is_available as mps_is_available
from torch.mps import empty_cache as mps_empty_cache
from asyncio import to_thread as async_to_thread

from app.models.chat_session import ChatSessionCreate, ChatSession
from app.models.chat_message import ChatMessageCreate, ChatMessage, ChatMessageRole
from app.models.user import User
from app.models.knowledge import Knowledge

from app.repositories.chat_session import ChatSessionRepository
from app.repositories.chat_message import ChatMessageRepository
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository
from app.repositories.knowledge import KnowledgeRepository
from app.repositories.vector import VectorRepository

from app.core.exceptions.app_exception import AppException
from app.core.messages import ErrorMessages
from app.core.constants import PermissionName
from app.core.config import settings

from app.services.embed import embed_chunks

from app.db.qdrant import app_qdrant_client


def _get_embedding_and_cleanup(text: str) -> List[float]:
    vector = embed_chunks([text])[0]

    gc_collect()

    if cuda_is_available():
        cuda_empty_cache()
    elif mps_is_available():
        mps_empty_cache()
    return vector


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @cached_property
    def chat_session_repo(self) -> ChatSessionRepository:
        return ChatSessionRepository(self.db)

    @cached_property
    def chat_message_repo(self) -> ChatMessageRepository:
        return ChatMessageRepository(self.db)

    @cached_property
    def role_repo(self) -> RoleRepository:
        return RoleRepository(self.db)

    @cached_property
    def permission_repo(self) -> PermissionRepository:
        return PermissionRepository(self.db)

    @cached_property
    def knowledge_repo(self) -> KnowledgeRepository:
        return KnowledgeRepository(self.db)

    @cached_property
    def vector_repo(self) -> VectorRepository:
        return VectorRepository(app_qdrant_client)

    async def create_chat_session(
        self, chat_session_create: ChatSessionCreate, current_user: User
    ) -> ChatSession:
        user_departments = await self.role_repo.get_user_departments(current_user.id)
        if not user_departments:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        user_department_ids = [department.id for department in user_departments]
        for id in chat_session_create.department_ids:
            if id not in user_department_ids:
                raise AppException(403, ErrorMessages.ACCESS_DENIED)

        chat_session = await self.chat_session_repo.create(
            chat_session_create, current_user.id
        )

        await self.db.commit()
        return chat_session

    async def read_chat_sessions(self, current_user: User) -> List[ChatSession]:
        return await self.chat_session_repo.get_chat_sessions(current_user.id)

    async def read_chat_messages(
        self, session_id: UUID, current_user: User
    ) -> List[ChatMessage]:
        user_sessions = await self.chat_session_repo.get_chat_sessions(current_user.id)
        if not user_sessions:
            raise AppException(404, ErrorMessages.CHAT_SESSIONS_NOT_FOUND)

        user_session_ids = [session.id for session in user_sessions]
        if session_id not in user_session_ids:
            raise AppException(403, ErrorMessages.ACCESS_DENIED)

        return await self.chat_session_repo.get_chat_session_messages(session_id)

    async def stream_chat_response(
        self, session_id: UUID, user_chat_message: ChatMessageCreate, current_user: User
    ) -> AsyncIterable[ChatMessage]:
        user_sessions = await self.chat_session_repo.get_chat_sessions(current_user.id)
        if not user_sessions:
            raise AppException(404, ErrorMessages.CHAT_SESSIONS_NOT_FOUND)

        user_session_ids = [session.id for session in user_sessions]
        if session_id not in user_session_ids:
            raise AppException(403, ErrorMessages.ACCESS_DENIED)

        chat_messages_history = (
            await self.chat_session_repo.get_chat_session_limit_messages(session_id, 10)
        )

        user_message = await self.chat_message_repo.create(
            session_id, user_chat_message
        )
        await self.chat_session_repo.touch_chat_session_timestamp(session_id)

        yield user_message

        # Role based
        chat_session = await self.chat_session_repo.get_by_id(session_id)
        if not chat_session:
            raise AppException(404, ErrorMessages.CHAT_SESSIONS_NOT_FOUND)

        knowledge_ids: List[str] = []
        for department_id in chat_session.department_ids:
            department = await self.role_repo.get_by_id(department_id)
            if not department:
                raise AppException(404, ErrorMessages.DEPARTMENT_NOT_FOUND)

            user_role = await self.role_repo.get_user_role_of_department(
                current_user, department
            )
            if not user_role:
                raise AppException(403, ErrorMessages.ROLE_ACCESS_BLOCK)

            child_roles = await self.role_repo.get_child_roles_of_role(user_role.id)
            for child_role in child_roles:
                if not await self.role_repo.can_user_edit_role(
                    current_user, child_role, strict_higher=True
                ):
                    user_permissions = (
                        await self.permission_repo.get_user_role_permissions(
                            current_user.id, child_role.id
                        )
                    )

                    if not user_permissions:
                        raise AppException(403, ErrorMessages.MISSING_PERMISSIONS)

                    if not self.permission_repo.has_all_permissions(
                        user_permissions, [PermissionName.VIEW]
                    ):
                        raise AppException(403, ErrorMessages.MISSING_PERMISSIONS)

                knowledges = await self.knowledge_repo.get_role_knowledges(
                    child_role.id
                )
                for k in knowledges:
                    knowledge_ids.append(str(k.id))

        # Embedding user message
        user_message_vector = await async_to_thread(
            _get_embedding_and_cleanup, user_chat_message.content
        )

        context_text = ""
        rs_knowledge_ids: List[str] = []

        if knowledge_ids:
            context_text, rs_knowledge_ids = await self.vector_repo.search_context(
                user_message_vector, knowledge_ids
            )

        system_prompt = f"""You are a helpful and intelligent Artificial Intelligence assistant.
        Your primary task is to answer the user's question using the <CONTEXT_DOCUMENT> below.

        RULES:
        1. DETECT LANGUAGE: You MUST detect the language of the user's question and write your ENTIRE response in that EXACT SAME LANGUAGE.
        2. RAG FIRST: Always try to answer based ONLY on the <CONTEXT_DOCUMENT>.
        3. LLM KNOWLEDGE FALLBACK: If the <CONTEXT_DOCUMENT> is empty or does NOT contain the answer, you MUST answer the question using your own internal general knowledge.
        4. MANDATORY DISCLAIMER: If you use your internal knowledge (Rule 3), you MUST start your response with a clear warning in the user's language.
        - Example warning (English): "⚠️ I could not find this information in the system documents. Answering based on AI general knowledge:\n\n"

        <CONTEXT_DOCUMENT>
        {context_text if context_text else "No documents match the current access rights."}
        </CONTEXT_DOCUMENT>
        """

        full_assistant_reply = ""
        ai_message_id = uuid4()

        # Top System Prompt
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Chat History
        for msg in chat_messages_history:
            messages.append({"role": msg.role.value, "content": msg.content})

        # Bottom Injection / Reminder
        messages.append(
            {
                "role": "system",
                "content": "Reminder: If the context document does NOT contain the answer to the next question, you MUST start your response with the '⚠️' warning in the user's language.",
            }
        )

        # Bottom-most
        messages.append({"role": "user", "content": user_chat_message.content})

        print(messages)

        ollama_client = AsyncClient(host=settings.OLLAMA_HOST)
        try:
            response_stream = await ollama_client.chat(  # type: ignore
                model="gemma4:e2b-it-q4_K_M",
                messages=messages,
                stream=True,
                options={"temperature": 0.0},
            )

            async for chunk in response_stream:
                content_chunk = chunk["message"]["content"]
                if content_chunk:
                    full_assistant_reply += content_chunk

                    yield ChatMessage(
                        id=ai_message_id,
                        role=ChatMessageRole.ASSISTANT,
                        content=content_chunk,
                        session_id=session_id,
                        knowledge_ids=[UUID(rs_id) for rs_id in rs_knowledge_ids],
                    )
        except Exception as e:
            yield ChatMessage(
                id=ai_message_id,
                role=ChatMessageRole.ASSISTANT,
                content=ErrorMessages.CHAT_ERROR + str(e),
                session_id=session_id,
                knowledge_ids=[UUID(rs_id) for rs_id in rs_knowledge_ids],
            )

        assistant_msg_create = ChatMessage(
            id=ai_message_id,
            role=ChatMessageRole.ASSISTANT,
            content=full_assistant_reply,
            session_id=session_id,
            knowledge_ids=[UUID(rs_id) for rs_id in rs_knowledge_ids],
        )

        self.db.add(assistant_msg_create)
        await self.db.flush()
        await self.chat_session_repo.touch_chat_session_timestamp(session_id)
        await self.db.commit()

    async def get_message_sources(
        self, session_id: UUID, message_id: UUID, current_user: User
    ) -> List[Knowledge]:
        user_sessions = await self.chat_session_repo.get_chat_sessions(current_user.id)
        if not user_sessions:
            raise AppException(404, ErrorMessages.CHAT_SESSIONS_NOT_FOUND)

        user_session_ids = [session.id for session in user_sessions]
        if session_id not in user_session_ids:
            raise AppException(403, ErrorMessages.ACCESS_DENIED)

        message = await self.chat_message_repo.get_by_id(message_id)
        if not message:
            raise AppException(404, ErrorMessages.CHAT_MESSAGE_NOT_FOUND)

        knowledges: List[Knowledge] = []
        for k_id in message.knowledge_ids:
            k = await self.knowledge_repo.get_by_id(k_id)
            if k:
                knowledges.append(k)

        return knowledges
