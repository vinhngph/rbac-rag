from sqlmodel import SQLModel, Field, Relationship, AutoString
from pydantic import EmailStr, HttpUrl
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.models.links import UserDepartmentRoleLink


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)
    name: str = Field(default="Unknown")

    avatar_url: Optional[HttpUrl] = Field(
        default=None, description="Avatar url.", sa_type=AutoString
    )


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str

    departments: List["Department"] = Relationship(back_populates="users", link_model=UserDepartmentRoleLink)  # type: ignore


class UserRegister(UserBase):
    plain_text_password: str


class UserLogin(SQLModel):
    email: EmailStr
    plain_text_password: str


class UserPublic(UserBase):
    id: UUID


class UserAT(SQLModel):
    sub: UUID
    exp: datetime
