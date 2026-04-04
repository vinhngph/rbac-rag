from sqlmodel import SQLModel, Field
from typing import Any
from uuid import UUID


class Model(SQLModel, table=True):
    __tablename__: Any = "users_roles"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
