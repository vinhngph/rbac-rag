from fastapi import UploadFile
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Tuple
from uuid import UUID
from functools import cached_property

from app.core.messages import ErrorMessages, SystemMessages
from app.core.constants import PermissionName, KnowledgeStatus
from app.core.exceptions.app_exception import AppException
from app.models.user import User
from app.models.knowledge import Knowledge, KnowledgeUpdate
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository
from app.repositories.knowledge import KnowledgeRepository
from app.services.zero_trust import ZeroTrust
from app.services.store import StoreService


class KnowledgeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @cached_property
    def role_repo(self) -> RoleRepository:
        return RoleRepository(self.db)

    @cached_property
    def permission_repo(self) -> PermissionRepository:
        return PermissionRepository(self.db)

    @cached_property
    def knowledge_repo(self) -> KnowledgeRepository:
        return KnowledgeRepository(self.db)

    async def create_knowledge(
        self,
        user: User,
        file: UploadFile,
        role_id: UUID,
    ) -> Knowledge:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        if not await self.role_repo.can_user_edit_role(user, role, strict_higher=True):
            user_permissions = await self.permission_repo.get_user_role_permissions(
                user.id, role_id
            )

            if not user_permissions:
                raise AppException(403, ErrorMessages.MISSING_PERMISSIONS)

            if not self.permission_repo.has_all_permissions(
                user_permissions, [PermissionName.EDIT, PermissionName.VIEW]
            ):
                raise AppException(403, ErrorMessages.MISSING_PERMISSIONS)

        zero_trust = ZeroTrust()
        knowledge = await zero_trust.execute_security_pipeline(file, user.id, role_id)

        await self.knowledge_repo.add_knowledge(knowledge)

        await self.db.commit()
        await self.db.refresh(knowledge)

        return knowledge

    async def get_role_knowledges(
        self,
        user: User,
        role_id: UUID,
    ) -> List[Knowledge]:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        if not await self.role_repo.can_user_edit_role(user, role, strict_higher=True):
            user_permissions = await self.permission_repo.get_user_role_permissions(
                user.id, role_id
            )

            if not user_permissions:
                raise AppException(403, ErrorMessages.MISSING_PERMISSIONS)

            if not self.permission_repo.has_all_permissions(
                user_permissions, [PermissionName.VIEW]
            ):
                raise AppException(403, ErrorMessages.MISSING_PERMISSIONS)

        return await self.knowledge_repo.get_role_knowledges(role_id)

    async def update_knowledge(
        self,
        user: User,
        knowledge_id: UUID,
        knowledge_update: KnowledgeUpdate,
    ) -> Knowledge:
        knowledge = await self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            raise AppException(404, ErrorMessages.KNOWLEDGE_NOT_FOUND)

        user_permissions = await self.permission_repo.get_user_role_permissions(
            user.id, knowledge.role_id
        )

        if not self.permission_repo.has_all_permissions(
            user_permissions, [PermissionName.VIEW, PermissionName.EDIT]
        ):
            raise AppException(403, ErrorMessages.MISSING_PERMISSIONS)

        if knowledge_update.role_id:
            if knowledge.role_id == knowledge_update.role_id:
                raise AppException(400, ErrorMessages.KNOWLEDGE_INVALID_MOVE)

            dest_role = await self.role_repo.get_by_id(knowledge_update.role_id)
            if not dest_role:
                raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

            if not await self.role_repo.can_user_edit_role(
                user, dest_role, strict_higher=False
            ):
                raise AppException(403, ErrorMessages.ROLE_ACCESS_BLOCK)

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
    ) -> bool:
        role = await self.role_repo.get_by_id(knowledge.role_id)
        if not role:
            raise AppException(404, ErrorMessages.ROLE_NOT_FOUND)

        if not await self.role_repo.can_user_edit_role(user, role, strict_higher=True):
            user_permissions = await self.permission_repo.get_user_role_permissions(
                user_id=user.id, role_id=knowledge.role_id
            )

            if not self.permission_repo.has_all_permissions(user_permissions, required):
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
    ) -> None:
        knowledge = await self.get_knowledge(knowledge_id)

        if not knowledge:
            raise AppException(404, "Knowledge not found")

        if not await self.can_user_access(
            user,
            knowledge,
            [PermissionName.EDIT, PermissionName.VIEW],
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

    async def get_knowledge_file(
        self, knowledge_id: UUID, current_user: User
    ) -> Tuple[str, Knowledge]:
        knowledge = await self.knowledge_repo.get_by_id(knowledge_id)
        if not knowledge:
            raise AppException(404, ErrorMessages.KNOWLEDGE_NOT_FOUND)

        user_permissions = await self.permission_repo.get_user_role_permissions(
            current_user.id, knowledge.role_id
        )

        if not self.permission_repo.has_all_permissions(
            user_permissions, [PermissionName.VIEW]
        ):
            raise AppException(403, ErrorMessages.MISSING_PERMISSIONS)

        store_service = StoreService()

        return (store_service.get_safe_path(knowledge.id), knowledge)
