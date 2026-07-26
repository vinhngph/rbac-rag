from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.role import Role
    from app.models.user import User


class UserRolePermissionLink(SQLModel, table=True):
    __tablename__: Any = "users_roles_permissions"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permissions.id", primary_key=True)

    user: "User" = Relationship(back_populates="role_links")
    role: "Role" = Relationship(back_populates="user_links")
    permission: "Permission" = Relationship(back_populates="user_links")
