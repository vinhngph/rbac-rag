from sqlmodel import SQLModel, Field
from uuid import UUID
from typing import Any


class RolePermissionLink(SQLModel, table=True):
    __tablename__: Any = "roles_permissions"

    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permissions.id", primary_key=True)


class UserDepartmentRoleLink(SQLModel, table=True):
    __tablename__: Any = "user_department_role"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    department_id: UUID = Field(foreign_key="departments.id", primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)


class KnowledgeRoleLink(SQLModel, table=True):
    __tablename__: Any = "knowledges_roles"

    knowledge_id: UUID = Field(foreign_key="knowledges.id", primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
