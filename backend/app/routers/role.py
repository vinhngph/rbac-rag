from fastapi import APIRouter, UploadFile, File, BackgroundTasks, status
from typing import List, Annotated
from uuid import UUID

from app.dependencies.current_user import CurrentUser
from app.models.knowledge import KnowledgeRead
from app.services.knowledge import UseKnowledgeService
from app.services.role import UseRoleService
from app.services.permission import UsePermissionService
from app.services.zero_trust import UseZeroTrust
from app.services.worker.knowledge import process_knowledge


router = APIRouter(prefix="/roles", tags=["Role Organization"])


@router.post(
    "/{role_id}/knowledges",
    response_model=KnowledgeRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_knowledge(
    role_id: UUID,
    file: Annotated[UploadFile, File()],
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    knowledge_service: UseKnowledgeService,
    role_service: UseRoleService,
    zero_trust: UseZeroTrust,
    permissions_service: UsePermissionService,
):
    knowledge = await knowledge_service.create_knowledge(
        user, file, role_id, role_service, zero_trust, permissions_service
    )

    background_tasks.add_task(process_knowledge, knowledge_id=knowledge.id)

    return knowledge


@router.get("/{role_id}/knowledges", response_model=List[KnowledgeRead])
async def get_role_knowledges(
    role_id: UUID,
    user: CurrentUser,
    knowledge_service: UseKnowledgeService,
    role_service: UseRoleService,
    permission_service: UsePermissionService,
):
    return await knowledge_service.get_role_knowledges_on_user(
        user, role_id, role_service, permission_service
    )
