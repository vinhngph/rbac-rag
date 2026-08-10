from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlmodel import AutoString, Column, DateTime, Field, Relationship, SQLModel

from app.core.types import NonEmptyString

if TYPE_CHECKING:
    from app.models.user import User


class Session(SQLModel, table=True):
    __tablename__: Any = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    refresh_token_hash: NonEmptyString
    device: str | None = Field(default=None, sa_type=AutoString)
    location: str | None = Field(default=None, sa_type=AutoString)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )

    user: "User" = Relationship(back_populates="sessions")
