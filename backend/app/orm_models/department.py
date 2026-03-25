from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import List

from app.orm_models.links import UserDepartmentRoleLink


class Department(SQLModel, table=True):
    __tablename__ = "departments"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)

    users: List["User"] = Relationship(  # type: ignore
        back_populates="departments", link_model=UserDepartmentRoleLink
    )

    roles: List["Role"] = Relationship(back_populates="department")  # type: ignore
