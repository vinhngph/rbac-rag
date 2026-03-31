from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any, List

from app.models.links import RolePermissionLink

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.department import Department


class Role(SQLModel, table=True):
    __tablename__: Any = "roles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default="Untitled role")
    department_id: UUID = Field(foreign_key="departments.id")

    permissions: List["Permission"] = Relationship(
        back_populates="roles", link_model=RolePermissionLink
    )

    department: "Department" = Relationship(back_populates="roles")
