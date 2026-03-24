from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List
from app.orm_models.links import UserRoleLink, DocumentPermissionLink


class Role(SQLModel, table=True):
    __tablename__ = "roles"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)

    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)  # type: ignore
    accessible_documents: List["Document"] = Relationship(  # type: ignore
        back_populates="allowed_roles", link_model=DocumentPermissionLink
    )
