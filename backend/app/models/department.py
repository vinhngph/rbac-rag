from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List

from app.models.links import UserDepartmentRoleLink


class DepartmentBase(SQLModel):
    name: str = Field(index=True)


class Department(DepartmentBase, table=True):
    __tablename__ = "departments"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    users: List["User"] = Relationship(  # type: ignore
        back_populates="departments", link_model=UserDepartmentRoleLink
    )

    roles: List["Role"] = Relationship(back_populates="department")  # type: ignore


class DepartmentRead(DepartmentBase):
    id: UUID
