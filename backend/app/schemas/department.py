from typing import List

from sqlmodel import SQLModel

from app.models.role import Role, RoleRead


class DepartmentContextRead(SQLModel):
    roles_chain: List[RoleRead]
    current_user_role: RoleRead


class DepartmentContext(SQLModel):
    roles_chain: List[Role]
    current_user_role: Role
