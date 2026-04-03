from sqlmodel import SQLModel, Field, Relationship, AutoString
from pydantic import EmailStr, HttpUrl
from typing import List, Optional
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any

from app.models.links import UserDepartmentRoleLink
from app.core.types import NonEmptyString

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.knowledge import Knowledge


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)
    name: NonEmptyString

    avatar_url: Optional[HttpUrl] = Field(
        default=None, description="Avatar url.", sa_type=AutoString
    )


class User(UserBase, table=True):
    __tablename__: Any = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str

    departments: List["Department"] = Relationship(
        back_populates="users", link_model=UserDepartmentRoleLink
    )
    knowledges: List["Knowledge"] = Relationship(back_populates="uploader")
    owned_departments: List["Department"] = Relationship(back_populates="owner")


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
