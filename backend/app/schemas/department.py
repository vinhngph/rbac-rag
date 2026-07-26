from sqlmodel import SQLModel

from app.models.role import Role, RoleRead


class DepartmentContextRead(SQLModel):
    roles_chain: list[RoleRead]
    current_user_role: RoleRead


class DepartmentContext(SQLModel):
    roles_chain: list[Role]
    current_user_role: Role
