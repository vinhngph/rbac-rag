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

        if knowledge_ids:
            context_text = await self.vector_repo.search_context(
                user_message_vector, knowledge_ids
            )

        system_prompt = f"""You are a strict data extraction assistant.
        Your ONLY job is to answer the user's question by extracting the exact information from the CONTEXT DOCUMENT below.

        RULES:
        1. ONLY use the information provided in the CONTEXT DOCUMENT. Do NOT use outside knowledge or personal knowledge.
        2. If the user asks for questions from the text, extract them EXACTLY word-for-word as they appear in the document. Do not rewrite or rephrase them.
        3. If the document does not contain the information to answer, you must output exactly: "I could not find the information in the system."

        <CONTEXT_DOCUMENT>
        {context_text if context_text else "No documents match the current access rights."}
        </CONTEXT_DOCUMENT>
        """

        full_assistant_reply = ""
        ai_message_id = uuid4()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_chat_message.content},
        ]

        ollama_client = AsyncClient(host=settings.OLLAMA_HOST)
        try:
            response_stream = await ollama_client.chat(  # type: ignore
                model="gemma2:2b",
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
                    )
        except Exception as e:
            yield ChatMessage(
                id=ai_message_id,
                role=ChatMessageRole.ASSISTANT,
                content=ErrorMessages.CHAT_ERROR + str(e),
                session_id=session_id,
            )

        assistant_msg_create = ChatMessage(
            role=ChatMessageRole.ASSISTANT,
            content=full_assistant_reply,
            session_id=session_id,
        )

        self.db.add(assistant_msg_create)
        await self.db.flush()
        await self.chat_session_repo.touch_chat_session_timestamp(session_id)
        await self.db.commit()
