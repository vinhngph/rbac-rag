from fastapi import Depends, UploadFile, HTTPException, status
from sqlmodel import select
from typing import Annotated, List
from uuid import UUID
from functools import cached_property

from app.dependencies.db_session import DB_Session
from app.core.messages import ErrorMessages, SystemMessages
from app.core.constants import PermissionName, KnowledgeStatus
from app.core.exceptions.app_exception import AppException
from app.models.user import User
from app.models.knowledge import Knowledge, KnowledgeUpdate
from app.repositories.role import RoleRepository
from app.services.role import RoleService
from app.services.zero_trust import ZeroTrust
from app.services.permission import PermissionService


class KnowledgeService:
    def __init__(self, db: DB_Session) -> None:
        self.db = db

    @cached_property
    def role_repo(self) -> RoleRepository:
        return RoleRepository(self.db)

    async def create_knowledge(
        self,
        user: User,
        file: UploadFile,
        role_id: UUID,
        role_service: RoleService,
        zero_trust: ZeroTrust,
        permissions_service: PermissionService,
    ) -> Knowledge:
        user_role = await role_service.get_user_role(user, role_id)

        user_permissions = await permissions_service.get_user_permissions_of_role(
            user, user_role
        )

        granted_permission_names = [p.name for p in user_permissions]

        if not permissions_service.has_all_permissions(
            granted_permission_names, [PermissionName.EDIT, PermissionName.VIEW]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorMessages.MISSING_PERMISSIONS,
            )

        knowledge = await zero_trust.execute_security_pipeline(file, user, user_role)

        self.db.add(knowledge)
        await self.db.commit()
        await self.db.refresh(knowledge)

        return knowledge

    async def get_role_knowledges_on_user(
        self,
        user: User,
        role_id: UUID,
        role_service: RoleService,
        permission_service: PermissionService,
    ) -> List[Knowledge]:
        user_role = await role_service.get_user_role(user, role_id)

        user_permissions = await permission_service.get_user_permissions_of_role(
            user, user_role
        )
        granted_permission_names = [p.name for p in user_permissions]

        if not permission_service.has_all_permissions(
            granted_permission_names, [PermissionName.VIEW]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorMessages.MISSING_PERMISSIONS,
            )

        stm = select(Knowledge).where(Knowledge.role_id == role_id)
        knowledges = (await self.db.exec(stm)).all()

        return list(knowledges)

    async def update_knowledge(
        self,
        user: User,
        knowledge_id: UUID,
        knowledge_update: KnowledgeUpdate,
        role_service: RoleService,
        permission_service: PermissionService,
    ) -> Knowledge:
        stm = select(Knowledge).where(Knowledge.id == knowledge_id)

        knowledge = (await self.db.exec(stm)).one_or_none()
        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.KNOWLEDGE_NOT_FOUND,
            )

        user_role = await role_service.get_user_role(user, knowledge.role_id)
        user_permissions = await permission_service.get_user_permissions_of_role(
            user, user_role
        )
        granted_permission_names = [p.name for p in user_permissions]

        if not permission_service.has_all_permissions(
            granted_permission_names, [PermissionName.VIEW, PermissionName.EDIT]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorMessages.MISSING_PERMISSIONS,
            )

        if update_role_id := knowledge_update.role_id:
            if not (update_role := await role_service.get_role(update_role_id)) or not (
                await role_service.is_children_of_role(update_role, user_role)
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=ErrorMessages.KNOWLEDGE_INVALID_MOVE,
                )

        update_data = knowledge_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(knowledge, key, value)

        self.db.add(knowledge)
        await self.db.commit()
        await self.db.refresh(knowledge)

        return knowledge

    async def can_user_access(
        self,
        user: User,
        knowledge: Knowledge,
        required: List[PermissionName],
        role_service: RoleService,
        permission_service: PermissionService,
    ) -> bool:
        user_role = await role_service.get_user_role(user, knowledge.role_id)
        user_permissions = await permission_service.get_user_permissions_of_role(
            user, user_role
        )
        granted_permission_names = [p.name for p in user_permissions]

        if not permission_service.has_all_permissions(
            granted_permission_names, required
        ):
            return False
        return True

    async def get_knowledge(self, knowledge_id: UUID) -> Knowledge | None:
        return (
            await self.db.exec(select(Knowledge).where(Knowledge.id == knowledge_id))
        ).one_or_none()

    async def delete_knowledge(
        self,
        user: User,
        knowledge_id: UUID,
        role_service: RoleService,
        permission_service: PermissionService,
    ) -> None:
        knowledge = await self.get_knowledge(knowledge_id)

        if not knowledge:
            raise AppException(404, "Knowledge not found")

        if not await self.can_user_access(
            user,
            knowledge,
            [PermissionName.EDIT, PermissionName.VIEW],
            role_service,
            permission_service,
        ):
            raise AppException(403, "Knowledge access denied.")

        trash_role = await self.role_repo.get_trash_role()
        if not trash_role:
            raise AppException(500, SystemMessages.DATABASE_SEED)

        if knowledge.role_id == trash_role.id:
            raise AppException(400, "Knowledge already in trash.")

        if knowledge.status not in [KnowledgeStatus.COMPLETED, KnowledgeStatus.FAILED]:
            raise AppException(400, "Knowledge is processing.")

        knowledge.original_role_id = knowledge.role_id
        knowledge.role_id = trash_role.id

        self.db.add(knowledge)
        await self.db.commit()


type UseKnowledgeService = Annotated[KnowledgeService, Depends(KnowledgeService)]
