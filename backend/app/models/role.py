from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any, List

from app.models.links import RolePermissionLink, KnowledgeRoleLink

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.department import Department
    from app.models.knowledge import Knowledge


class Role(SQLModel, table=True):
    __tablename__: Any = "roles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default="Untitled role")
    department_id: UUID = Field(foreign_key="departments.id")

    permissions: List["Permission"] = Relationship(
        back_populates="roles", link_model=RolePermissionLink
    )

    department: "Department" = Relationship(back_populates="roles")

    knowledges: List["Knowledge"] = Relationship(
        link_model=KnowledgeRoleLink, back_populates="allowed_roles"
    )
