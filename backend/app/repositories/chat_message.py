from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.base import BaseRepository
from app.models.chat_message import ChatMessage


class ChatMessageRepository(BaseRepository[ChatMessage]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(ChatMessage, db)
