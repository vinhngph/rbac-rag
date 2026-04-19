from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from app.repositories.base import BaseRepository

from app.models.chat_message import ChatMessage, ChatMessageCreate


class ChatMessageRepository(BaseRepository[ChatMessage]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(ChatMessage, db)

    async def create(
        self, session_id: UUID, chat_message_create: ChatMessageCreate
    ) -> ChatMessage:
        chat_message = ChatMessage(
            role=chat_message_create.role,
            content=chat_message_create.content,
            session_id=session_id,
        )

        self.db.add(chat_message)
        await self.db.flush()
        await self.db.refresh(chat_message)

        return chat_message
