from sqlmodel import SQLModel, Field, Relationship
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from app.orm_models.links import UserDepartmentRoleLink


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    name: str


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str

    departments: List["Department"] = Relationship(back_populates="users", link_model=UserDepartmentRoleLink)  # type: ignore


class UserCreate(UserBase):
    password: str


class UserAT(UserBase):
    sub: UUID
    exp: datetime
