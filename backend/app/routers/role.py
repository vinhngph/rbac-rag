from fastapi import APIRouter, UploadFile, File, BackgroundTasks, status
from typing import List, Annotated
from uuid import UUID

from app.dependencies.current_user import CurrentUser
from app.models.knowledge import KnowledgeRead
from app.models.role import RoleRead, RoleCreate, RoleUpdate
from app.schemas.member import MemberRead, MemberCreate, MemberUpdate
from app.services.knowledge import UseKnowledgeService
from app.services.role import UseRoleService
from app.services.permission import UsePermissionService
from app.services.zero_trust import UseZeroTrust
from app.services.worker.knowledge import process_knowledge


router = APIRouter(prefix="/roles", tags=["Role Organization"])


@router.post("/", response_model=RoleRead)
async def create_role(
    role_create: RoleCreate, user: CurrentUser, role_service: UseRoleService
):
    return await role_service.create_role(user, role_create)


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    user: CurrentUser,
    role_service: UseRoleService,
):
    return await role_service.update_role(user, role_id, role_update)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: UUID, user: CurrentUser, role_service: UseRoleService):
    return await role_service.delete_role(user, role_id)


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


@router.get("/{role_id}/members", response_model=List[MemberRead])
async def get_role_members(
    role_id: UUID, user: CurrentUser, role_service: UseRoleService
):
    return await role_service.get_members_of_role(user, role_id)


@router.post("/{role_id}/members", response_model=MemberRead)
async def add_member_to_role(
    role_id: UUID,
    member_create: MemberCreate,
    user: CurrentUser,
    role_service: UseRoleService,
):
    return await role_service.add_member_to_role(user, member_create, role_id)


@router.delete("/{role_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_role(
    role_id: UUID, member_id: UUID, user: CurrentUser, role_service: UseRoleService
):
    return await role_service.delete_member_from_role(user, member_id, role_id)


@router.patch("/{role_id}/members", response_model=MemberRead)
async def update_member_permissions_in_role(
    role_id: UUID,
    member_update: MemberUpdate,
    user: CurrentUser,
    role_service: UseRoleService,
):
    return await role_service.update_user_role_permissions(user, role_id, member_update)
