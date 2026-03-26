from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List

from app.models.links import RolePermissionLink


class Permission(SQLModel, table=True):
    __tablename__ = "permissions"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)

    roles: List["Role"] = Relationship(  # type: ignore
        back_populates="permissions", link_model=RolePermissionLink
    )
