from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.knowledge import Knowledge
    from app.models.links import UserRolePermissionLink


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

    original_parent_id: Optional[UUID] = Field(
        default=None, foreign_key="roles.id", nullable=True
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

    knowledges: List["Knowledge"] = Relationship(back_populates="role")

    user_links: List["UserRolePermissionLink"] = Relationship(back_populates="role")

    @property
    def users(self) -> List["User"]:
        unique_users = {
            link.user.id: link.user for link in self.user_links if link.user
        }
        return list(unique_users.values())


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id: UUID


class RoleUpdate(SQLModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None


class RootRoleBase(SQLModel):
    name: str = "Untitled"


class RootRoleCreate(RootRoleBase):
    pass


class RootRoleRead(RootRoleBase):
    id: UUID


class RootRoleUpdate(SQLModel):
    name: Optional[str] = None
