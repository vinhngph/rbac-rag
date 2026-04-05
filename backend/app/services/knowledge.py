from fastapi import Depends, UploadFile, HTTPException, status
from typing import Annotated
from uuid import UUID

from app.dependencies.db_session import DB_Session
from app.core.constants import PermissionName
from app.models.user import User
from app.models.knowledge import Knowledge
from app.services.role import RoleService
from app.services.zero_trust import ZeroTrust
from app.services.permission import PermissionService


class KnowledgeService:
    def __init__(self, db: DB_Session) -> None:
        self.db = db

    async def create_knowledge(
        self,
        user: User,
        file: UploadFile,
        role_id: UUID,
        role_service: RoleService,
        zero_trust: ZeroTrust,
        permissions_service: PermissionService,
    ) -> Knowledge:
        user_role = await role_service.get_role(role_id)

        user_permissions = await permissions_service.get_user_permissions_of_role(
            user, user_role
        )

        granted_permission_names = [p.name for p in user_permissions]

        if not permissions_service.has_all_permissions(
            granted_permission_names, [PermissionName.EDIT, PermissionName.VIEW]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to upload knowledge.",
            )

        knowledge = await zero_trust.execute_security_pipeline(file, user, user_role)

        self.db.add(knowledge)
        await self.db.commit()
        await self.db.refresh(knowledge)

        return knowledge


type UseKnowledgeService = Annotated[KnowledgeService, Depends(KnowledgeService)]
