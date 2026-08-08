from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from pydantic import EmailStr, HttpUrl, field_validator
from sqlmodel import AutoString, Field, Relationship, SQLModel

from app.core.types import NonEmptyString

if TYPE_CHECKING:
    from app.models.chat_session import ChatSession
    from app.models.knowledge import Knowledge
    from app.models.links import UserRolePermissionLink
    from app.models.role import Role


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)
    name: NonEmptyString

    avatar_url: HttpUrl | None = Field(
        default=None, description="Avatar url.", sa_type=AutoString
    )


class User(UserBase, table=True):
    __tablename__: Any = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: NonEmptyString

    role_links: list["UserRolePermissionLink"] = Relationship(back_populates="user")

    knowledges: list["Knowledge"] = Relationship(back_populates="author")

    chats: list["ChatSession"] = Relationship(back_populates="user")

    @property
    def roles(self) -> list["Role"]:
        unique_roles = {
            link.role.id: link.role for link in self.role_links if link.role
        }
        return list(unique_roles.values())


class UserRegister(UserBase):
    plain_text_password: NonEmptyString
    turnstile_token: NonEmptyString

    @field_validator("plain_text_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserLogin(SQLModel):
    email: EmailStr
    plain_text_password: NonEmptyString
    turnstile_token: NonEmptyString


class UserRead(UserBase):
    id: UUID


class UserAT(SQLModel):
    sub: NonEmptyString
    exp: int
    iat: int
