from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col
from typing import List
from uuid import UUID

from app.repositories.base import BaseRepository
from app.models.permission import Permission
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
