from fastapi import Depends, HTTPException, status
from sqlmodel import select, col
from typing import List, Annotated
from uuid import UUID

from app.dependencies.db_session import DB_Session
from app.core.messages import ErrorMessages
from app.models.user import User
from app.models.role import Role, RootRoleCreate, RootRoleUpdate
from app.models.links import UserRolePermissionLink
from app.services.permission import PermissionService
from app.services.trash import TrashService


class RoleService:
    def __init__(self, db: DB_Session):
        self.db = db

    async def get_user_role(self, user: User, role_id: UUID) -> Role:
        stm = (
            select(Role)
            .where(Role.id == role_id)
            .join(UserRolePermissionLink)
            .where(UserRolePermissionLink.user_id == user.id)
            .distinct()
        )

        role = (await self.db.exec(stm)).one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorMessages.ROLE_ACCESS_BLOCK,
            )

        root_role = await self.get_root_of_role(role)
        if root_role.name == "Trash":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorMessages.ROLE_ACCESS_BLOCK,
            )

        return role

    async def get_user_roles(self, user: User) -> List[Role]:
        stm = (
            select(Role)
            .join(UserRolePermissionLink)
            .where(UserRolePermissionLink.user_id == user.id)
            .distinct()
        )
        return list((await self.db.exec(stm)).all())

    async def get_user_departments(
        self, user: User, trash_service: TrashService
    ) -> List[Role]:
        user_role_ids = [role.id for role in (await self.get_user_roles(user))]

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

        trash = await trash_service.get_trash_role()

        stmt = (
            select(Role)
            .join(hierarchy, col(Role.id) == hierarchy.c.id)
            .where(col(Role.parent_id).is_(None))
            .where(col(Role.id) != trash.id)
            .distinct()
        )

        return list((await self.db.exec(stmt)).all())

    async def get_user_role_of_department(
        self, user: User, department_id: UUID
    ) -> Role:
        dept_hierarchy = (
            select(Role.id)
            .where(col(Role.id) == department_id)
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

        user_role = (await self.db.exec(stm)).one_or_none()

        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorMessages.ROLE_ACCESS_BLOCK,
            )

        return user_role

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
            return role

        return root

    async def create_user_department(
        self,
        user: User,
        new_department: RootRoleCreate,
        permission_service: PermissionService,
    ) -> Role:
        permissions = await permission_service.get_permissions()

        department = Role(name=new_department.name, parent_id=None)

        self.db.add(department)
        await self.db.flush()

        links = [
            UserRolePermissionLink(
                user_id=user.id, role_id=department.id, permission_id=permission.id
            )
            for permission in permissions
        ]
        self.db.add_all(links)
        await self.db.commit()
        await self.db.refresh(department)

        return department

    async def get_department(self, user: User, department_id: UUID) -> List[Role]:
        user_role = await self.get_user_role_of_department(user, department_id)

        visible_hierarchy = (
            select(Role.id)
            .where(col(Role.id) == user_role.id)
            .cte(name="visible_hierarchy_cte", recursive=True)
        )

        visible_hierarchy = visible_hierarchy.union_all(
            select(Role.id).join(
                visible_hierarchy, col(Role.parent_id) == visible_hierarchy.c.id
            )
        )

        stm = select(Role).join(
            visible_hierarchy, col(Role.id) == visible_hierarchy.c.id
        )

        return list((await self.db.exec(stm)).all())

    async def update_department(
        self, user: User, department_id: UUID, update_data: RootRoleUpdate
    ) -> Role:
        department = await self.db.get(Role, department_id)
        if (not department) or (department.parent_id is not None):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found."
            )

        user_role = await self.get_user_role_of_department(user, department_id)
        if user_role.id != department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update information of this department.",
            )

        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(department, key, value)

        self.db.add(department)
        await self.db.commit()
        await self.db.refresh(department)

        return department

    async def delete_department(
        self, user: User, department_id: UUID, trash_service: TrashService
    ) -> None:
        department = await self.db.get(Role, department_id)
        if (not department) or (department.parent_id is not None):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Department not found."
            )
        user_role = await self.get_user_role_of_department(user, department_id)
        if user_role.id != department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this department.",
            )

        await trash_service.move_to_trash(department)

        return None

    async def get_role(self, role_id: UUID) -> Role | None:
        return (
            await self.db.exec(select(Role).where(Role.id == role_id))
        ).one_or_none()

    async def is_children_of_role(self, child_role: Role, parent_role: Role) -> bool:
        if (
            (child_role.parent_id is None)
            or (child_role.parent_id == parent_role.parent_id)
            or (child_role.id == parent_role.id)
        ):
            return False
        elif child_role.parent_id == parent_role.id:
            return True

        hierarchy = (
            select(Role.parent_id)
            .where(Role.id == child_role.id)
            .cte(name="check_parents_cte", recursive=True)
        )
        hierarchy = hierarchy.union_all(
            select(Role.parent_id).join(
                hierarchy, col(Role.id) == hierarchy.c.parent_id
            )
        )

        stm = select(hierarchy.c.parent_id).where(
            hierarchy.c.parent_id == parent_role.id
        )
        rs = (await self.db.exec(stm)).first()

        return rs is not None


type UseRoleService = Annotated[RoleService, Depends(RoleService)]
