from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col, update
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from app.repositories.base import BaseRepository
from app.models.chat_session import ChatSession, ChatSessionCreate
from app.models.chat_message import ChatMessage


class ChatSessionRepository(BaseRepository[ChatSession]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(ChatSession, db)

    async def create(
        self, chat_session_create: ChatSessionCreate, user_id: UUID
    ) -> ChatSession:
        chat_session = ChatSession(
            user_id=user_id,
            department_ids=chat_session_create.department_ids,
            title=chat_session_create.title,
        )

        self.db.add(chat_session)
        await self.db.flush()
        await self.db.refresh(chat_session)

        return chat_session

    async def touch_chat_session_timestamp(self, session_id: UUID):
        stm = (
            update(ChatSession)
            .where(col(ChatSession.id) == session_id)
            .values({ChatSession.updated_at: datetime.now(timezone.utc)})
        )
        await self.db.exec(stm)

    async def get_chat_sessions(self, user_id: UUID) -> List[ChatSession]:
        stm = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(col(ChatSession.updated_at).desc())
        )

        return list((await self.db.exec(stm)).all())

    async def get_chat_session_messages(self, session_id: UUID) -> List[ChatMessage]:
        stm = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(col(ChatMessage.updated_at).asc())
        )
        return list((await self.db.exec(stm)).all())

    async def get_chat_session_limit_messages(
        self, session_id: UUID, limit: int = 5
    ) -> List[ChatMessage]:
        stm = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(col(ChatMessage.updated_at).desc())
            .limit(limit)
        )

        messages = list((await self.db.exec(stm)).all())
        messages.reverse()

        return messages
