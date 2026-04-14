from fastapi import APIRouter, UploadFile, File, BackgroundTasks, status
from typing import List, Annotated
from uuid import UUID

from app.api.dependencies.current_user import CurrentUser
from app.api.dependencies.db_session import DB_Session

from app.models.knowledge import KnowledgeRead
from app.models.role import RoleRead, RoleCreate, RoleUpdate

from app.schemas.member import MemberRead, MemberCreate, MemberUpdate

from app.services.knowledge import KnowledgeService
from app.services.role import RoleService
from app.services.worker.knowledge import process_knowledge


router = APIRouter(prefix="/roles", tags=["Role Organization"])


@router.post("/", response_model=RoleRead)
async def create_role(role_create: RoleCreate, user: CurrentUser, db: DB_Session):
    role_service = RoleService(db)
    return await role_service.create_role(user, role_create)


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: UUID, role_update: RoleUpdate, user: CurrentUser, db: DB_Session
):
    role_service = RoleService(db)
    return await role_service.update_role(user, role_id, role_update)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: UUID, user: CurrentUser, db: DB_Session):
    role_service = RoleService(db)
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
    db: DB_Session,
):
    knowledge_service = KnowledgeService(db)
    knowledge = await knowledge_service.create_knowledge(user, file, role_id)

    background_tasks.add_task(process_knowledge, knowledge_id=knowledge.id)

    return knowledge


@router.get("/{role_id}/knowledges", response_model=List[KnowledgeRead])
async def get_role_knowledges(role_id: UUID, user: CurrentUser, db: DB_Session):
    knowledge_service = KnowledgeService(db)
    return await knowledge_service.get_role_knowledges(user, role_id)


@router.get("/{role_id}/members", response_model=List[MemberRead])
async def get_role_members(role_id: UUID, user: CurrentUser, db: DB_Session):
    role_service = RoleService(db)
    return await role_service.get_members_of_role(user, role_id)


@router.post("/{role_id}/members", response_model=MemberRead)
async def add_member_to_role(
    role_id: UUID, member_create: MemberCreate, user: CurrentUser, db: DB_Session
):
    role_service = RoleService(db)
    return await role_service.add_member_to_role(user, member_create, role_id)


@router.delete("/{role_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_role(
    role_id: UUID, member_id: UUID, user: CurrentUser, db: DB_Session
):
    role_service = RoleService(db)
    return await role_service.delete_member_from_role(user, member_id, role_id)


@router.patch("/{role_id}/members", response_model=MemberRead)
async def update_member_permissions_in_role(
    role_id: UUID, member_update: MemberUpdate, user: CurrentUser, db: DB_Session
):
    role_service = RoleService(db)
    return await role_service.update_user_role_permissions(user, role_id, member_update)
