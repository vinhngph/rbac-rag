from sqlmodel import SQLModel, Field
from uuid import UUID


class RolePermissionLink(SQLModel, table=True):
    __tablename__ = "roles_permissions"  # type: ignore

    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permissions.id", primary_key=True)


class UserDepartmentRoleLink(SQLModel, table=True):
    __tablename__ = "user_department_role"  # type: ignore

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    department_id: UUID = Field(foreign_key="departments.id", primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
