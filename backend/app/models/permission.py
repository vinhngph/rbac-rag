from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any, List

from app.core.constants import PermissionName
from app.models.links import RolePermissionLink


if TYPE_CHECKING:
    from app.models.role import Role


class PermissionBase(SQLModel):
    name: PermissionName = Field(unique=True, index=True)


class Permission(PermissionBase, table=True):
    __tablename__: Any = "permissions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    roles: List["Role"] = Relationship(
        back_populates="permissions", link_model=RolePermissionLink.Model
    )


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    id: UUID
