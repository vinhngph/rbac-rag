from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any, List, Optional

from app.models.links import RolePermissionLink, UserRoleLink

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.permission import Permission
    from app.models.knowledge import Knowledge


class RoleBase(SQLModel):
    name: str = Field(default="Untitled")

    # None -> root role
    # uuid -> child role
    parent_id: Optional[UUID] = Field(
        default=None,
        foreign_key="roles.id",
        index=True,
        nullable=True,
        description="NULL means this is the root role in the department.",
    )


class Role(RoleBase, table=True):
    __tablename__: Any = "roles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    parent: Optional["Role"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "foreign_keys": "[Role.parent_id]",
            "remote_side": "Role.id",
        },
    )

    children: List["Role"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"foreign_keys": "[Role.parent_id]"},
    )

    members: List["User"] = Relationship(
        back_populates="roles", link_model=UserRoleLink
    )

    permissions: List["Permission"] = Relationship(
        back_populates="roles", link_model=RolePermissionLink
    )

    knowledges: List["Knowledge"] = Relationship(back_populates="role")


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    pass


class RoleUpdate(SQLModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
