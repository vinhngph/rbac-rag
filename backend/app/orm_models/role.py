from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List

from app.orm_models.links import RolePermissionLink


class Role(SQLModel, table=True):
    __tablename__ = "roles"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default="Untitled role")
    department_id: UUID = Field(foreign_key="departments.id")

    permissions: List["Permission"] = Relationship(  # type: ignore
        back_populates="roles", link_model=RolePermissionLink
    )

    department: "Department" = Relationship(back_populates="roles")  # type: ignore
