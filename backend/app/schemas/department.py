from sqlmodel import SQLModel
from typing import List

from app.models.role import RoleRead, Role


class DepartmentContextRead(SQLModel):
    roles_chain: List[RoleRead]
    current_user_role: RoleRead


class DepartmentContext(SQLModel):
    roles_chain: List[Role]
    current_user_role: Role
