from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Optional, List, TypedDict

from app.models.user import UserRead, User
from app.core.constants import PermissionName


class MemberRead(UserRead):
    permissions: Optional[List[PermissionName]] = None


class MemberDict(TypedDict):
    user: User
    permissions: List[PermissionName]


class MemberCreate(SQLModel):
    email: EmailStr
    permissions: List[PermissionName]
