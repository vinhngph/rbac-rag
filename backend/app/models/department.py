from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, List, Optional, Any

from app.models.links import UserDepartmentRoleLink
from app.core.types import NonEmptyString

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.role import Role
    from app.models.knowledge import Knowledge


class DepartmentBase(SQLModel):
    name: NonEmptyString = Field(index=True)


class Department(DepartmentBase, table=True):
    __tablename__: Any = "departments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    owner_id: UUID = Field(foreign_key="users.id", index=True)
    status: bool = Field(default=True, index=True)

    users: List["User"] = Relationship(
        back_populates="departments", link_model=UserDepartmentRoleLink
    )
    roles: List["Role"] = Relationship(back_populates="department")
    knowledges: List["Knowledge"] = Relationship(back_populates="department")
    owner: "User" = Relationship(back_populates="owned_departments")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    id: UUID
    owner_id: UUID
    status: bool


class DepartmentUpdate(SQLModel):
    name: Optional[str] = None
