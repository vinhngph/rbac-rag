from sqlmodel import SQLModel, Field, Relationship, Column, DateTime
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from app.core.types import NonEmptyString
from app.core.constants import KnowledgeStatus, FileType

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.user import User


class KnowledgeBase(SQLModel):
    title: NonEmptyString = Field(index=True)
    file_type: FileType = Field(description=f"{[t.value for t in FileType]}")
    status: KnowledgeStatus = Field(
        default=KnowledgeStatus.SCANNING,
        description=f"{[s.value for s in KnowledgeStatus]}",
    )

    department_id: UUID = Field(foreign_key="departments.id")
    uploader_id: UUID = Field(foreign_key="users.id")


class Knowledge(KnowledgeBase, table=True):
    __tablename__: Any = "knowledges"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )

    department: "Department" = Relationship(back_populates="knowledges")
    uploader: "User" = Relationship(back_populates="knowledges")


class KnowledgeRead(KnowledgeBase):
    id: UUID
    created_at: datetime
