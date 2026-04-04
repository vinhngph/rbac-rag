from sqlmodel import SQLModel, Field
from typing import Any
from uuid import UUID


class Model(SQLModel, table=True):
    __tablename__: Any = "roles_permissions"

    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permissions.id", primary_key=True)
