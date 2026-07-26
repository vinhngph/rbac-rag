from typing import List, Optional, TypedDict
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel

from app.core.constants import PermissionName
from app.models.user import User, UserRead


class MemberRead(UserRead):
    permissions: Optional[List[PermissionName]] = None


class MemberUpdate(SQLModel):
    id: UUID
    permissions: List[PermissionName]


class MemberDict(TypedDict):
    user: User
    permissions: List[PermissionName]


class MemberCreate(SQLModel):
    email: EmailStr
    permissions: List[PermissionName]
