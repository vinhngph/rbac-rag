from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any, List

from app.core.constants import PermissionName

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.links import UserRolePermissionLink


class PermissionBase(SQLModel):
    name: PermissionName = Field(unique=True, index=True)


class Permission(PermissionBase, table=True):
    __tablename__: Any = "permissions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_links: List["UserRolePermissionLink"] = Relationship(
        back_populates="permission"
    )

    @property
    def users(self) -> List["User"]:
        unique_users = {
            link.user.id: link.user for link in self.user_links if link.user
        }
        return list(unique_users.values())


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    id: UUID
