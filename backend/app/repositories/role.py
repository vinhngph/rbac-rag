from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col, delete
from typing import Optional, List
from uuid import UUID

from app.repositories.base import BaseRepository
from app.models.links import UserRolePermissionLink
from app.models.role import Role
from app.models.user import User


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Role, db)

    async def get_root_of_role(self, role: Role) -> Role:
        if not role.parent_id:
            return role

        hierarchy = (
            select(Role.id, Role.parent_id)
            .where(Role.id == role.id)
            .cte(name="root_of_role_cte", recursive=True)
        )
        hierarchy = hierarchy.union_all(
            select(Role.id, Role.parent_id).join(
                hierarchy, col(Role.id) == hierarchy.c.parent_id
            )
        )

        stm = (
            select(Role)
            .join(hierarchy, col(Role.id) == hierarchy.c.id)
            .where(col(Role.parent_id).is_(None))
            .distinct()
        )

        root = (await self.db.exec(stm)).one_or_none()
        if not root:
            raise ValueError(
                f"Data corruption detected: Role {role.id} has no valid root."
            )

        return root

    async def get_user_role_of_department(
        self, user: User, department: Role
    ) -> Optional[Role]:
        dept_hierarchy = (
            select(Role.id)
            .where(col(Role.id) == department.id)
            .cte(name="dept_hierarchy_cte", recursive=True)
        )
        dept_hierarchy = dept_hierarchy.union_all(
            select(Role.id).join(
                dept_hierarchy, col(Role.parent_id) == dept_hierarchy.c.id
            )
        )

        stm = (
            select(Role)
            .join(UserRolePermissionLink)
            .join(dept_hierarchy, col(Role.id) == dept_hierarchy.c.id)
            .where(UserRolePermissionLink.user_id == user.id)
            .distinct()
        )

        return (await self.db.exec(stm)).one_or_none()

    async def add_user_to_role(
        self, user: User, permission_ids: List[UUID], role: Role
    ) -> None:
        links = [
            UserRolePermissionLink(
                user_id=user.id, role_id=role.id, permission_id=permission_id
            )
            for permission_id in permission_ids
        ]

        self.db.add_all(links)

    async def delete_user_role(self, user: User, role: Role) -> None:
        stm = delete(UserRolePermissionLink).where(
            col(UserRolePermissionLink.user_id) == user.id,
            col(UserRolePermissionLink.role_id) == role.id,
        )
        await self.db.exec(stm)
