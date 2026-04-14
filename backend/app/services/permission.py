from fastapi import HTTPException, status
from sqlmodel import select, col
from typing import List

from app.api.dependencies.db_session import DB_Session
from app.core.constants import PermissionName
from app.core.messages import SystemMessages
from app.models.permission import Permission


class PermissionService:
    def __init__(self, db: DB_Session):
        self.db = db

    async def get_permissions(self) -> List[Permission]:
        default_permission_names = [p.value for p in PermissionName]
        stm = select(Permission).where(
            col(Permission.name).in_(default_permission_names)
        )
        permissions = (await self.db.exec(statement=stm)).all()

        if len(permissions) != len(default_permission_names):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=SystemMessages.DATABASE_SEED,
            )

        return list(permissions)
