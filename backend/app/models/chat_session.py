from sqlmodel import (
    SQLModel,
    Field,
    Column,
    DateTime,
    Relationship,
    ARRAY,
    UUID as sa_UUID,
)
from typing import TYPE_CHECKING, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timezone

if TYPE_CHECKING:
    from app.models.chat_message import ChatMessage
    from app.models.user import User


class ChatSessionBase(SQLModel):
    department_ids: List[UUID] = Field(sa_column=Column(ARRAY(sa_UUID(as_uuid=True))))

    title: str = Field(default="Untitled chat")


class ChatSession(ChatSessionBase, table=True):
    __tablename__: Any = "chat_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_id: UUID = Field(foreign_key="users.id")

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )

    messages: List["ChatMessage"] = Relationship(back_populates="session")
    user: "User" = Relationship(back_populates="chats")


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionRead(ChatSessionBase):
    user_id: UUID
    updated_at: datetime


class ChatSessionUpdate(ChatSessionBase):
    pass
