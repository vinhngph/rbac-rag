from sqlmodel.ext.asyncio.session import AsyncSession
from functools import cached_property
from typing import List
from uuid import UUID

from app.models.chat_session import ChatSessionCreate, ChatSession
from app.models.chat_message import ChatMessageCreate, ChatMessage
from app.models.user import User

from app.repositories.chat_session import ChatSessionRepository
from app.repositories.chat_message import ChatMessageRepository
from app.repositories.role import RoleRepository

from app.core.exceptions.app_exception import AppException
from app.core.messages import ErrorMessages


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

    async def create_chat_message(
        self,
        session_id: UUID,
        chat_message_create: ChatMessageCreate,
        current_user: User,
    ) -> ChatMessage:
        user_sessions = await self.chat_session_repo.get_chat_sessions(current_user.id)
        if not user_sessions:
            raise AppException(404, ErrorMessages.CHAT_SESSIONS_NOT_FOUND)

        user_session_ids = [session.id for session in user_sessions]
        if session_id not in user_session_ids:
            raise AppException(403, ErrorMessages.ACCESS_DENIED)

        chat_message = await self.chat_message_repo.create(
            session_id, chat_message_create
        )
        await self.chat_session_repo.touch_chat_session_timestamp(session_id)

        await self.db.commit()
        return chat_message

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
