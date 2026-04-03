from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, List, Any

from app.models.links import RolePermissionLink
from app.core.constants import PermissionName

if TYPE_CHECKING:
    from app.models.role import Role


class Permission(SQLModel, table=True):
    __tablename__: Any = "permissions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: PermissionName = Field(unique=True, index=True)

    roles: List["Role"] = Relationship(
        back_populates="permissions", link_model=RolePermissionLink
    )
