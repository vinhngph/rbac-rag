from fastapi import Depends, HTTPException, status
from sqlmodel import select, col
from typing import Annotated, List

from app.dependencies.db_session import DB_Session
from app.core.constants import PermissionName
from app.core.messages import SystemMessages
from app.models.permission import Permission
from app.models.user import User
from app.models.role import Role
from app.models.links import UserRolePermissionLink


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

    async def get_user_permissions_of_role(
        self, user: User, role: Role
    ) -> List[Permission]:
        stm = (
            select(Permission)
            .join(UserRolePermissionLink)
            .where(
                UserRolePermissionLink.user_id == user.id,
                UserRolePermissionLink.role_id == role.id,
            )
        )
        
        return list((await self.db.exec(stm)).all())

    def has_any_permission(
        self, granted: List[PermissionName], required: List[PermissionName]
    ) -> bool:
        return not set(granted).isdisjoint(required)

    def has_all_permissions(
        self, granted: List[PermissionName], required: List[PermissionName]
    ) -> bool:
        return set(required).issubset(set(granted))


type UsePermissionService = Annotated[PermissionService, Depends(PermissionService)]
