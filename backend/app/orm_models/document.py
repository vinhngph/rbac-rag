from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from app.orm_models.links import DocumentPermissionLink


class DocumentBase(SQLModel):
    title: Optional[str] = Field(default=None, description="Document title")


class Document(DocumentBase, table=True):
    __tablename__ = "documents"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_by: UUID = Field(default=None, foreign_key="users.id")

    creator: "User" = Relationship(back_populates="documents")  # type: ignore
    allowed_roles: List["Role"] = Relationship(  # type: ignore
        back_populates="accessible_documents", link_model=DocumentPermissionLink
    )


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: UUID
    created_by: UUID
