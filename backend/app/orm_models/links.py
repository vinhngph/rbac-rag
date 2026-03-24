from sqlmodel import SQLModel, Field
from uuid import UUID


class UserRoleLink(SQLModel, table=True):
    __tablename__ = "user_roles"  # type: ignore

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)


class DocumentPermissionLink(SQLModel, table=True):
    __tablename__ = "document_permissions"  # type: ignore

    document_id: UUID = Field(foreign_key="documents.id", primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
