from fastapi import Depends, HTTPException, status
from sqlmodel import select, col, exists
from typing import List, Annotated
from uuid import UUID
from functools import cached_property

from app.dependencies.db_session import DB_Session
from app.core.exceptions.app_exception import AppException
from app.core.messages import ErrorMessages
from app.models.user import User
from app.models.permission import Permission
from app.models.role import Role, RootRoleCreate, RootRoleUpdate, RoleCreate, RoleUpdate
from app.models.links import UserRolePermissionLink
from app.schemas.member import MemberRead, MemberDict, MemberCreate
from app.services.permission import PermissionService
from app.services.trash import TrashService
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository


class RoleService:
    def __init__(self, db: DB_Session):
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

        root_role = await self.role_repo.get_root_of_role(role)
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
        department = await self.role_repo.get_by_id(department_id)
        if not department:
            raise AppException(404, ErrorMessages.DEPARTMENT_NOT_FOUND)

        user_role = await self.role_repo.get_user_role_of_department(user, department)
        if not user_role:
            raise AppException(403, ErrorMessages.ROLE_ACCESS_BLOCK)

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

    async def delete_department(
        self, user: User, department_id: UUID, trash_service: TrashService
    ) -> None:
        department = await self.role_repo.get_by_id(department_id)
        if not department:
            raise AppException(404, ErrorMessages.DEPARTMENT_NOT_FOUND)

        user_role = await self.role_repo.get_user_role_of_department(user, department)
        if not user_role:
            raise AppException(403, ErrorMessages.ROLE_ACCESS_BLOCK)

        if user_role.id != department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this department.",
            )

        await trash_service.move_role_to_trash(department)

        return None

    async def get_role(self, role_id: UUID) -> Role:
        role = (
            await self.db.exec(select(Role).where(Role.id == role_id))
        ).one_or_none()

        if not role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        return role

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

        if await self.is_children_of_role(current_role, user_role):
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

    async def create_role(self, user: User, role_create: RoleCreate) -> Role:
        parent_role = await self.db.get(Role, role_create.parent_id)
        if not parent_role:
            raise AppException(404, "Role not found.")

        if not (await self.can_user_edit_role(user, parent_role, strict_higher=False)):
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

        if not (await self.can_user_edit_role(user, role, strict_higher=True)):
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
                    not await self.can_user_edit_role(
                        user, dest_role, strict_higher=False
                    )
                )
                or (await self.is_children_of_role(dest_role, role))
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

        if not await self.can_user_edit_role(user, role, strict_higher=True):
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

            if not await self.can_user_edit_role(
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


type UseRoleService = Annotated[RoleService, Depends(RoleService)]
