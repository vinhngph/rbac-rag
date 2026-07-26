from typing import TypedDict
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel

from app.core.constants import PermissionName
from app.models.user import User, UserRead


class MemberRead(UserRead):
    permissions: list[PermissionName] | None = None


class MemberUpdate(SQLModel):
    id: UUID
    permissions: list[PermissionName]


class MemberDict(TypedDict):
    user: User
    permissions: list[PermissionName]


class MemberCreate(SQLModel):
    email: EmailStr
    permissions: list[PermissionName]
