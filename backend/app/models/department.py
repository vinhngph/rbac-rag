from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List, Optional

from app.models.links import UserDepartmentRoleLink
from app.core.types import NonEmptyString


class DepartmentBase(SQLModel):
    name: NonEmptyString = Field(index=True)


class Department(DepartmentBase, table=True):
    __tablename__ = "departments"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    users: List["User"] = Relationship(  # type: ignore
        back_populates="departments", link_model=UserDepartmentRoleLink
    )

    roles: List["Role"] = Relationship(back_populates="department")  # type: ignore


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    id: UUID


class DepartmentUpdate(SQLModel):
    name: Optional[str] = None
