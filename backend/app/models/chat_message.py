from sqlmodel import SQLModel, Field, Text, Relationship, Column, DateTime
from uuid import uuid4, UUID
from typing import TYPE_CHECKING, Any
from enum import Enum
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.models.chat_session import ChatSession


class ChatMessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessageBase(SQLModel):
    role: ChatMessageRole = Field(nullable=False)

    content: str = Field(sa_column=Column(Text, nullable=False))


class ChatMessage(ChatMessageBase, table=True):
    __tablename__: Any = "chat_messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )

    session_id: UUID = Field(foreign_key="chat_sessions.id")

    session: "ChatSession" = Relationship(back_populates="messages")


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageRead(ChatMessageBase):
    id: UUID
    session_id: UUID


class ChatMessageUpdate(ChatMessageBase):
    pass
