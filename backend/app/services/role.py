from fastapi import HTTPException, status
from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from uuid import UUID
from functools import cached_property

from app.core.exceptions.app_exception import AppException
from app.core.messages import ErrorMessages, SystemMessages
from app.core.constants import PermissionName
from app.models.user import User
from app.models.permission import Permission
from app.models.role import Role, RootRoleCreate, RootRoleUpdate, RoleCreate, RoleUpdate
from app.models.links import UserRolePermissionLink
from app.schemas.member import MemberRead, MemberDict, MemberCreate, MemberUpdate
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @cached_property
    def user_repo(self) -> UserRepository:
        return UserRepository(self.db)

    @cached_property
    def role_repo(self) -> RoleRepository:
        return RoleRepository(self.db)

    @cached_property
    def permission_repo(self) -> PermissionRepository:
        return PermissionRepository(self.db)

    async def get_user_departments(self, user: User) -> List[Role]:
        user_role_ids = [
            role.id for role in (await self.role_repo.get_user_roles(user.id))
        ]

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

        trash = await self.role_repo.get_trash_role()
        if not trash:
            raise AppException(500, SystemMessages.DATABASE_SEED)

        stmt = (
            select(Role)
            .join(hierarchy, col(Role.id) == hierarchy.c.id)
            .where(col(Role.parent_id).is_(None))
            .where(col(Role.id) != trash.id)
            .distinct()
        )

        return list((await self.db.exec(stmt)).all())

    async def create_user_department(
        self,
        user: User,
        new_department: RootRoleCreate,
    ) -> Role:
        department = Role(name=new_department.name, parent_id=None)

        self.role_repo.create(department)

        await self.db.flush()

        permission_ids = await self.permission_repo.get_ids_by_name(
            [PermissionName.EDIT, PermissionName.VIEW]
        )

        await self.role_repo.add_user_role_permissions(
            user.id, department.id, permission_ids
        )

        await self.db.commit()
        await self.db.refresh(department)

        return department

    async def get_department(self, user: User, department_id: UUID) -> List[Role]:
        department = await self.role_repo.get_by_id(department_id)
        if not department:
            raise AppException(404, ErrorMessages.DEPARTMENT_NOT_FOUND)

        user_role = await self.role_repo.get_user_role_of_department(user, department)
        if not user_role:
            raise AppException(403, ErrorMessages.ROLE_ACCESS_BLOCK)

        if department.id == user_role.id:
            return await self.role_repo.get_roles_chain_top_down(department.id)
        else:
            return await self.role_repo.get_roles_chain_bottom_up(user_role.id)

    async def update_department(
        self, user: User, department_id: UUID, update_data: RootRoleUpdate
    ) -> Role:
        department = await self.role_repo.get_by_id(department_id)
        if not department:
            raise AppException(404, ErrorMessages.DEPARTMENT_NOT_FOUND)

        user_role = await self.role_repo.get_user_role_of_department(user, department)
        if not user_role:
            raise AppException(403, ErrorMessages.ROLE_ACCESS_BLOCK)

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

    async def delete_department(self, user: User, department_id: UUID) -> None:
        department = await self.role_repo.get_by_id(department_id)
        if (not department) or (
            await self.role_repo.get_root_of_role(department)
        ).id != department.id:
            raise AppException(404, ErrorMessages.DEPARTMENT_NOT_FOUND)

        if not await self.role_repo.can_user_edit_role(
            user, department, strict_higher=False
        ):
            raise AppException(403, ErrorMessages.ROLE_ACCESS_BLOCK)

        trash = await self.role_repo.get_trash_role()
        if not trash:
            raise AppException(500, SystemMessages.DATABASE_SEED)

        if (department.id == trash.id) or (department.parent_id == trash.id):
            raise AppException(400, ErrorMessages.DELETE_DENIED)

        await self.role_repo.move_role_to_trash(department, trash)
        await self.db.commit()

        return None

    async def get_role(self, role_id: UUID) -> Role:
        role = (
            await self.db.exec(select(Role).where(Role.id == role_id))
        ).one_or_none()

        if not role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        return role

    async def get_members_of_role(self, user: User, role_id: UUID) -> List[MemberRead]:
        current_role = await self.role_repo.get_by_id(role_id)
        if not current_role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        department = await self.role_repo.get_root_of_role(current_role)
        if not department:
            raise AppException(404, ErrorMessages.DEPARTMENT_NOT_FOUND)

        user_role = await self.role_repo.get_user_role_of_department(user, department)
        if not user_role:
            raise AppException(403, ErrorMessages.ROLE_ACCESS_BLOCK)

        members: List[MemberRead] = []

        if await self.role_repo.is_children_of_role(current_role.id, user_role.id):
            stm = (
                select(User, Permission)
                .select_from(User)
                .join(UserRolePermissionLink)
                .join(Permission)
                .where(UserRolePermissionLink.role_id == current_role.id)
            )
            rs = (await self.db.exec(stm)).all()

            users_map: dict[UUID, MemberDict] = {}
            for user, permission in rs:
                if user.id not in users_map:
                    users_map[user.id] = {"user": user, "permissions": []}
                users_map[user.id]["permissions"].append(permission.name)

            for user_data in users_map.values():
                u = user_data["user"]
                members.append(
                    MemberRead(
                        id=u.id,
                        email=u.email,
                        name=u.name,
                        avatar_url=u.avatar_url,
                        permissions=user_data["permissions"],
                    )
                )
        else:
            stm = (
                select(User)
                .join(UserRolePermissionLink)
                .where(UserRolePermissionLink.role_id == current_role.id)
                .distinct()
            )
            rs = (await self.db.exec(stm)).all()

            for user in rs:
                members.append(
                    MemberRead(
                        id=user.id,
                        email=user.email,
                        name=user.name,
                        avatar_url=user.avatar_url,
                    )
                )

        return members

    async def create_role(self, user: User, role_create: RoleCreate) -> Role:
        parent_role = await self.db.get(Role, role_create.parent_id)
        if not parent_role:
            raise AppException(404, "Role not found.")

        if not (
            await self.role_repo.can_user_edit_role(
                user, parent_role, strict_higher=False
            )
        ):
            raise AppException(403, "Access denied.")

        new_role = Role.model_validate(role_create)

        self.db.add(new_role)
        await self.db.commit()
        await self.db.refresh(new_role)

        return new_role

    async def update_role(
        self, user: User, role_id: UUID, role_update: RoleUpdate
    ) -> Role:
        role = await self.get_role(role_id)

        if not (
            await self.role_repo.can_user_edit_role(user, role, strict_higher=True)
        ):
            raise AppException(403, ErrorMessages.ACCESS_DENIED)

        update_dict = role_update.model_dump(exclude_unset=True)

        if "parent_id" in update_dict:
            new_parent_id = update_dict["parent_id"]

            if new_parent_id is None:
                raise AppException(403, ErrorMessages.ACCESS_DENIED)

            dest_role = await self.get_role(new_parent_id)

            if (
                role.id == dest_role.id
                or (
                    not await self.role_repo.can_user_edit_role(
                        user, dest_role, strict_higher=False
                    )
                )
                or (await self.role_repo.is_children_of_role(dest_role.id, role.id))
            ):
                raise AppException(403, ErrorMessages.ACCESS_DENIED)

            be_move_root_role = await self.role_repo.get_root_of_role(role)
            dest_move_root_role = await self.role_repo.get_root_of_role(dest_role)

            if be_move_root_role.id != dest_move_root_role.id:
                raise AppException(403, ErrorMessages.ACCESS_DENIED)

            role.original_parent_id = dest_role.id

        for key, value in update_dict.items():
            setattr(role, key, value)

        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)

        return role

    async def add_member_to_role(
        self, user: User, member_create: MemberCreate, role_id: UUID
    ) -> MemberRead:
        """
        Only add member to this role if current user's role level is higher.
        """
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        if not await self.role_repo.can_user_edit_role(user, role, strict_higher=True):
            raise AppException(403, ErrorMessages.ACCESS_DENIED)

        department = await self.role_repo.get_root_of_role(role)

        member_user = await self.user_repo.get_user_by_email(member_create.email)
        if not member_user:
            raise AppException(404, f"User {member_create.email} not found.")

        member_role_in_department = await self.role_repo.get_user_role_of_department(
            member_user, department
        )
        permission_ids = await self.permission_repo.get_ids_by_name(
            member_create.permissions
        )
        if not member_role_in_department:
            # New member
            await self.role_repo.add_user_to_role(member_user, permission_ids, role)
        else:
            # Old member
            if member_role_in_department.id == role.id:
                raise AppException(400, ErrorMessages.MEMBER_ADD_ERROR)

            if not await self.role_repo.can_user_edit_role(
                user, member_role_in_department, strict_higher=True
            ):
                raise AppException(403, ErrorMessages.ACCESS_DENIED)

            await self.role_repo.delete_user_role(
                member_user, member_role_in_department
            )
            await self.role_repo.add_user_to_role(member_user, permission_ids, role)

        await self.db.commit()

        return MemberRead(
            id=member_user.id,
            email=member_user.email,
            name=member_user.name,
            permissions=member_create.permissions,
        )

    async def delete_member_from_role(
        self, user: User, member_id: UUID, role_id: UUID
    ) -> None:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        if not await self.role_repo.can_user_edit_role(user, role, strict_higher=True):
            raise AppException(403, ErrorMessages.ACCESS_DENIED)

        member_user = await self.user_repo.get_by_id(member_id)
        if not member_user:
            raise AppException(404, ErrorMessages.USER_NOT_FOUND)

        department = await self.role_repo.get_root_of_role(role)

        member_role_in_department = await self.role_repo.get_user_role_of_department(
            member_user, department
        )

        if not member_role_in_department:
            raise AppException(400, ErrorMessages.MEMBER_NOT_FOUND)

        if member_role_in_department.id != role.id:
            raise AppException(400, ErrorMessages.MEMBER_ROLE_CONFLICT)

        await self.role_repo.delete_user_role(member_user, member_role_in_department)

        await self.db.commit()

    async def update_user_role_permissions(
        self, user: User, role_id: UUID, member_update: MemberUpdate
    ) -> MemberRead:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        if not await self.role_repo.can_user_edit_role(user, role, strict_higher=True):
            raise AppException(403, ErrorMessages.ROLE_UPDATE_DENIED)

        department = await self.role_repo.get_root_of_role(role)

        member_user = await self.user_repo.get_by_id(member_update.id)
        if not member_user:
            raise AppException(404, ErrorMessages.MEMBER_NOT_FOUND)

        member_role = await self.role_repo.get_user_role_of_department(
            member_user, department
        )
        if not member_role:
            raise AppException(403, ErrorMessages.ROLE_ACCESS_BLOCK)

        if member_role.id != role_id:
            raise AppException(403, ErrorMessages.MEMBER_ROLE_CONFLICT)

        permission_ids = await self.permission_repo.get_ids_by_name(
            member_update.permissions
        )
        await self.role_repo.delete_user_role_permissions(member_user.id, role.id)
        await self.role_repo.add_user_role_permissions(
            member_user.id, role.id, permission_ids
        )

        await self.db.commit()

        return MemberRead(
            id=member_user.id,
            email=member_user.email,
            name=member_user.name,
            permissions=member_update.permissions,
        )

    async def delete_role(self, user: User, role_id: UUID) -> None:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        if not await self.role_repo.can_user_edit_role(user, role, strict_higher=True):
            raise AppException(403, ErrorMessages.ROLE_UPDATE_DENIED)

        trash = await self.role_repo.get_trash_role()
        if not trash:
            raise AppException(500, SystemMessages.DATABASE_SEED)

        if (trash.id == role_id) or (role.parent_id == trash.id):
            raise AppException(403, ErrorMessages.DELETE_DENIED)

        await self.role_repo.move_role_to_trash(role, trash)
        await self.db.commit()

        return None
