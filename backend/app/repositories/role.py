from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col, delete, exists, literal
from typing import Optional, List
from uuid import UUID

from app.repositories.base import BaseRepository
from app.models.links import UserRolePermissionLink
from app.models.role import Role
from app.models.user import User


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Role, db)

    def create(self, role: Role) -> Role:
        self.db.add(role)
        return role

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

    async def can_user_edit_role(
        self, user: User, role: Role, strict_higher: bool
    ) -> bool:
        """
        - strict_higher=False: Use for CREATE child role.
        - strict_higher=True: Use for EDIT this role.
        """
        start_node_id = role.parent_id if strict_higher else role.id

        if strict_higher and not start_node_id:
            return False

        # Can user access parent
        hierarchy = (
            select(Role.id, Role.parent_id)
            .where(Role.id == start_node_id)
            .cte(name="is_user_parent_of_role_cte", recursive=True)
        )
        hierarchy = hierarchy.union_all(
            select(Role.id, Role.parent_id).join(
                hierarchy, col(Role.id) == hierarchy.c.parent_id
            )
        )
        stm = select(
            exists(
                select(1)
                .select_from(UserRolePermissionLink)
                .join(
                    hierarchy,
                    col(UserRolePermissionLink.role_id) == hierarchy.c.id,
                )
                .where(UserRolePermissionLink.user_id == user.id)
            )
        )
        return bool(await self.db.scalar(stm))

    async def delete_user_role_permissions(
        self, user_id: UUID, role_id: UUID, permission_ids: List[UUID] | None = None
    ) -> None:
        stm = delete(UserRolePermissionLink).where(
            col(UserRolePermissionLink.user_id) == user_id,
            col(UserRolePermissionLink.role_id) == role_id,
        )

        if permission_ids:
            stm = stm.where(
                col(UserRolePermissionLink.permission_id).in_(permission_ids)
            )

        await self.db.exec(stm)

    async def add_user_role_permissions(
        self, user_id: UUID, role_id: UUID, permission_ids: List[UUID]
    ) -> None:
        links = [
            UserRolePermissionLink(
                user_id=user_id, role_id=role_id, permission_id=permission_id
            )
            for permission_id in permission_ids
        ]
        self.db.add_all(links)

    async def get_trash_role(self) -> Role | None:
        stm = select(Role).where(Role.name == "Trash")
        return (await self.db.exec(stm)).one_or_none()

    async def move_role_to_trash(self, role: Role, trash: Role) -> None:
        role.original_parent_id = role.parent_id
        role.parent_id = trash.id

        self.db.add(role)

    async def is_children_of_role(
        self, child_role_id: UUID, parent_role_id: UUID
    ) -> bool:
        hierarchy = (
            select(Role.parent_id)
            .where(Role.id == child_role_id)
            .cte(name="check_parents_cte", recursive=True)
        )
        hierarchy = hierarchy.union_all(
            select(Role.parent_id).join(
                hierarchy, col(Role.id) == hierarchy.c.parent_id
            )
        )

        stm = select(hierarchy.c.parent_id).where(
            hierarchy.c.parent_id == parent_role_id
        )
        rs = (await self.db.exec(stm)).first()

        return rs is not None

    async def get_user_roles(self, user_id: UUID) -> List[Role]:
        stm = (
            select(Role)
            .join(UserRolePermissionLink)
            .where(UserRolePermissionLink.user_id == user_id)
            .distinct()
        )
        return list((await self.db.exec(stm)).all())

    async def get_roles_chain_bottom_up(self, from_role_id: UUID) -> List[Role]:
        hierarchy = (
            select(Role.id, Role.parent_id, literal(0).label("level"))
            .where(col(Role.id) == from_role_id)
            .cte(name="get_roles_chain_bottom_up_cte", recursive=True)
        )
        hierarchy = hierarchy.union_all(
            select(
                Role.id, Role.parent_id, (hierarchy.c.level + 1).label("level")
            ).join(hierarchy, col(Role.id) == hierarchy.c.parent_id)
        )
        stm = (
            select(Role)
            .join(hierarchy, col(Role.id) == hierarchy.c.id)
            .order_by(hierarchy.c.level.desc())
        )
        return list((await self.db.exec(stm)).all())

    async def get_roles_chain_top_down(self, root_role_id: UUID) -> List[Role]:
        hierarchy = (
            select(Role.id, Role.parent_id, literal(0).label("level"))
            .where(col(Role.id) == root_role_id)
            .cte("get_roles_chain_top_down_cte", recursive=True)
        )
        hierarchy = hierarchy.union_all(
            select(
                Role.id, Role.parent_id, (hierarchy.c.level + 1).label("level")
            ).join(hierarchy, col(Role.parent_id) == hierarchy.c.id)
        )
        stm = (
            select(Role)
            .join(hierarchy, col(Role.id) == hierarchy.c.id)
            .order_by(hierarchy.c.level.asc())
        )
        return list((await self.db.exec(stm)).all())

    async def get_user_departments(self, user_id: UUID) -> List[Role]:
        user_role_ids = [role.id for role in (await self.get_user_roles(user_id))]

        if not user_role_ids:
            return []

        hierarchy = (
            select(Role.id, Role.parent_id)
            .where(col(Role.id).in_(user_role_ids))
            .cte(name="user_departments_cte", recursive=True)
        )

        hierarchy = hierarchy.union_all(
            select(Role.id, Role.parent_id).join(
                hierarchy, col(Role.id) == hierarchy.c.parent_id
            )
        )

        trash = await self.get_trash_role()
        if not trash:
            return []

        stmt = (
            select(Role)
            .join(hierarchy, col(Role.id) == hierarchy.c.id)
            .where(col(Role.parent_id).is_(None))
            .where(col(Role.id) != trash.id)
            .distinct()
        )

        return list((await self.db.exec(stmt)).all())
