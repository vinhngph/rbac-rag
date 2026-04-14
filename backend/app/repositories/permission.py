from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col
from typing import List
from uuid import UUID

from app.repositories.base import BaseRepository
from app.models.permission import Permission
from app.models.links.user_role_permission import UserRolePermissionLink
from app.core.constants import PermissionName


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Permission, db)

    async def get_ids_by_name(
        self, permission_names: List[PermissionName]
    ) -> List[UUID]:
        if not permission_names:
            return []

        stm = select(Permission.id).where(col(Permission.name).in_(permission_names))
        return list((await self.db.exec(stm)).all())

    async def get_user_role_permissions(
        self, user_id: UUID, role_id: UUID
    ) -> List[PermissionName]:
        stm = (
            select(Permission.name)
            .join(UserRolePermissionLink)
            .where(
                UserRolePermissionLink.user_id == user_id,
                UserRolePermissionLink.role_id == role_id,
            )
        )

        rs = (await self.db.exec(stm)).all()

        return [PermissionName(p) for p in rs]

    def has_all_permissions(
        self, granted: List[PermissionName], required: List[PermissionName]
    ) -> bool:
        return set(required).issubset(set(granted))
