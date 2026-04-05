from sqlmodel import SQLModel, Field, Relationship, AutoString
from pydantic import EmailStr, HttpUrl
from typing import List, Optional
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any

from app.core.types import NonEmptyString

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.knowledge import Knowledge
    from app.models.links import UserRolePermissionLink


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)
    name: NonEmptyString

    avatar_url: Optional[HttpUrl] = Field(
        default=None, description="Avatar url.", sa_type=AutoString
    )


class User(UserBase, table=True):
    __tablename__: Any = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: NonEmptyString

    role_links: List["UserRolePermissionLink"] = Relationship(back_populates="user")

    knowledges: List["Knowledge"] = Relationship(back_populates="author")

    @property
    def roles(self) -> List["Role"]:
        unique_roles = {
            link.role.id: link.role for link in self.role_links if link.role
        }
        return list(unique_roles.values())


class UserRegister(UserBase):
    plain_text_password: NonEmptyString


class UserLogin(SQLModel):
    email: EmailStr
    plain_text_password: NonEmptyString


class UserRead(UserBase):
    id: UUID


class UserAT(SQLModel):
    sub: str
    exp: int
    iat: int
