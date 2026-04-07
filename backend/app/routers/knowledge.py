from fastapi import (
    APIRouter,
    status,
    UploadFile,
    File,
    BackgroundTasks,
    Header,
    HTTPException,
)
from fastapi.sse import EventSourceResponse, ServerSentEvent
from collections.abc import AsyncIterable
from uuid import UUID
from typing import Annotated, List
from json import dumps as json_dumps
from asyncio import sleep as async_sleep

from app.dependencies.current_user import CurrentUser
from app.dependencies.db_session import DB_Session
from app.models.knowledge import KnowledgeRead, KnowledgeUpdate
from app.core.messages import ErrorMessages
from app.core.constants import PermissionName, KnowledgeStatus
from app.services.worker.knowledge import process_knowledge
from app.services.knowledge import UseKnowledgeService
from app.services.role import UseRoleService
from app.services.zero_trust import UseZeroTrust
from app.services.permission import UsePermissionService


router = APIRouter(prefix="/roles/{role_id}/knowledges", tags=["Knowledge Base"])


@router.get("/", response_model=List[KnowledgeRead])
async def get_role_knowledges_on_user(
    role_id: UUID,
    user: CurrentUser,
    knowledge_service: UseKnowledgeService,
    role_service: UseRoleService,
    permission_service: UsePermissionService,
):
    return await knowledge_service.get_role_knowledges_on_user(
        user, role_id, role_service, permission_service
    )


@router.post("/", response_model=KnowledgeRead, status_code=status.HTTP_201_CREATED)
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


@router.patch("/{knowledge_id}", response_model=KnowledgeRead)
async def update_knowledge(
    role_id: UUID,
    knowledge_id: UUID,
    knowledge_update: KnowledgeUpdate,
    user: CurrentUser,
    knowledge_service: UseKnowledgeService,
    role_service: UseRoleService,
    permission_service: UsePermissionService,
):
    return await knowledge_service.update_knowledge(
        user, role_id, knowledge_id, knowledge_update, role_service, permission_service
    )


@router.get("/{knowledge_id}/status", response_class=EventSourceResponse)
async def stream_knowledge_status(
    role_id: UUID,
    knowledge_id: UUID,
    knowledge_service: UseKnowledgeService,
    role_service: UseRoleService,
    permission_service: UsePermissionService,
    user: CurrentUser,
    db: DB_Session,
    last_event_id: Annotated[str | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    knowledge = await knowledge_service.get_knowledge(knowledge_id)

    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.KNOWLEDGE_NOT_FOUND,
        )

    if knowledge.role_id != role_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMessages.KNOWLEDGE_BLOCK,
        )

    if not await knowledge_service.can_user_access(
        user, knowledge, [PermissionName.VIEW], role_service, permission_service
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMessages.MISSING_PERMISSIONS,
        )

    last_sent_status = last_event_id
    while True:
        current_status_value = knowledge.status.value

        if current_status_value != last_sent_status:
            yield ServerSentEvent(
                event="status_update",
                data=json_dumps({"status": current_status_value}),
                id=current_status_value,
                retry=3000,
            )
            last_sent_status = current_status_value

        if knowledge.status in [
            KnowledgeStatus.COMPLETED,
            KnowledgeStatus.FAILED,
        ]:
            break

        await async_sleep(2)
        await db.refresh(knowledge)
