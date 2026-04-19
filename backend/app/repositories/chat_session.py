from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from app.repositories.base import BaseRepository
from app.models.chat_session import ChatSession, ChatSessionCreate


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
