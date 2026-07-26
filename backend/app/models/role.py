from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.knowledge import Knowledge
    from app.models.links import UserRolePermissionLink
    from app.models.user import User


class RoleBase(SQLModel):
    name: str = Field(default="Untitled")

    # None -> root role
    # uuid -> child role
    parent_id: UUID | None = Field(
        default=None,
        foreign_key="roles.id",
        index=True,
        nullable=True,
        description="NULL means this is the root role in the department.",
    )

    original_parent_id: UUID | None = Field(
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

    children: list["Role"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"foreign_keys": "[Role.parent_id]"},
    )

    knowledges: list["Knowledge"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"foreign_keys": "[Knowledge.role_id]"},
    )

    user_links: list["UserRolePermissionLink"] = Relationship(back_populates="role")

    @property
    def users(self) -> list["User"]:
        unique_users = {
            link.user.id: link.user for link in self.user_links if link.user
        }
        return list(unique_users.values())


class RoleCreate(SQLModel):
    name: str = "Untitled"
    parent_id: UUID


class RoleRead(RoleBase):
    id: UUID


class RoleUpdate(SQLModel):
    name: str | None = None
    parent_id: UUID | None = None


class RootRoleBase(SQLModel):
    name: str = "Untitled"


class RootRoleCreate(RootRoleBase):
    pass


class RootRoleRead(RootRoleBase):
    id: UUID


class RootRoleUpdate(SQLModel):
    name: str | None = None
