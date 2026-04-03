from fastapi import (
    APIRouter,
    status,
    BackgroundTasks,
    UploadFile,
    HTTPException,
    File,
    Header,
    Form,
)
from fastapi.sse import EventSourceResponse, ServerSentEvent
from sqlmodel import or_, col
from sqlalchemy.orm import selectinload
from collections.abc import AsyncIterable
from uuid import UUID
from typing import Annotated, List, cast, Any
from json import dumps as json_dumps
from asyncio import sleep as async_sleep
from sqlmodel import select, col

from app.models.knowledge import (
    KnowledgeRead,
    Knowledge,
    KnowledgeUpdate,
    KnowledgeUpdateBase,
)
from app.models.role import Role
from app.models.department import Department
from app.models.links import UserDepartmentRoleLink
from app.db.session import DB_Session
from app.dependencies import CurrentUser, Allow
from app.services.zero_trust import zero_trust
from app.services.worker.knowledge import process_knowledge
from app.core.constants import KnowledgeStatus

router = APIRouter(
    prefix="/departments/{department_id}/knowledges", tags=["Knowledge Base"]
)


@router.get("/", response_model=List[Knowledge])
async def get_knowledges(
    department_id: UUID, user: CurrentUser, db: DB_Session, _can_view: Allow.VIEW
):
    department = await db.get(Department, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found."
        )

    query = select(Knowledge).where(Knowledge.department_id == department_id)

    if department.owner_id == user.id:
        user_roles_query = select(UserDepartmentRoleLink.role_id).where(
            UserDepartmentRoleLink.department_id == department.id,
            UserDepartmentRoleLink.user_id == user.id,
        )
        role_ids = (await db.exec(user_roles_query)).all()

        query = query.where(
            or_(
                # Public knowledge
                ~col(Knowledge.allowed_roles).any(),
                # Roles based knowledge
                col(Knowledge.allowed_roles).any(col(Role.id).in_(role_ids)),
            )
        )

    return (await db.exec(query)).unique().all()


@router.post("/", response_model=KnowledgeRead, status_code=status.HTTP_201_CREATED)
async def upload_knowledge(
    department_id: UUID,
    file: Annotated[UploadFile, File()],
    background_tasks: BackgroundTasks,
    db: DB_Session,
    user: CurrentUser,
    _can_edit: Allow.EDIT,
    allowed_role_ids: Annotated[List[UUID] | None, Form()] = None,
):
    try:
        knowledge = await zero_trust.execute_security_pipeline(
            file, user, department_id
        )
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Security Error: {str(e)}"
        )

    if allowed_role_ids:
        query = select(Role).where(
            col(Role.id).in_(allowed_role_ids),
            col(Role.department_id) == department_id,
        )
        valid_roles = (await db.exec(query)).all()

        if len(valid_roles) != len(allowed_role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid allowed_role_ids",
            )
        else:
            knowledge.allowed_roles = list(valid_roles)

    db.add(knowledge)
    await db.commit()
    await db.refresh(knowledge)

    background_tasks.add_task(process_knowledge, knowledge_id=knowledge.id)

    return knowledge


@router.patch("/{knowledge_id}", response_model=KnowledgeRead)
async def update_knowledge_informations(
    department_id: UUID,
    knowledge_id: UUID,
    knowledge_update: KnowledgeUpdate,
    user: CurrentUser,
    db: DB_Session,
):
    stm = (
        select(Knowledge)
        .where(Knowledge.id == knowledge_id)
        .options(selectinload(cast(Any, Knowledge.allowed_roles)))
    )
    knowledge = (await db.exec(stm)).one_or_none()

    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge not found."
        )

    update_data = knowledge_update.model_dump(
        exclude_unset=True, include=set(KnowledgeUpdateBase.model_fields)
    )

    for key, value in update_data.items():
        setattr(knowledge, key, value)

    if role_ids_in := knowledge_update.allowed_role_ids:
        query = select(Role).where(
            col(Role.id).in_(role_ids_in),
            col(Role.department_id) == department_id,
        )
        valid_roles = (await db.exec(query)).all()

        if len(valid_roles) != len(role_ids_in):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid allowed_role_ids",
            )
        else:
            knowledge.allowed_roles = list(valid_roles)
    else:
        knowledge.allowed_roles = []

    db.add(knowledge)
    await db.commit()
    await db.refresh(knowledge)

    return knowledge


@router.get("/{knowledge_id}/status", response_class=EventSourceResponse)
async def stream_knowledge_status(
    department_id: UUID,
    knowledge_id: UUID,
    db: DB_Session,
    _can_view: Allow.VIEW,
    last_event_id: Annotated[str | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    last_sent_status = last_event_id

    knowledge = await db.get(Knowledge, knowledge_id)
    if not knowledge:
        yield ServerSentEvent(
            event="error", data=json_dumps({"error": "File not found."}), id="error"
        )
        return
    while True:
        current_status = knowledge.status.value

        if current_status != last_sent_status:
            yield ServerSentEvent(
                event="status_update",
                data=json_dumps({"status": current_status}),
                id=current_status,
                retry=3000,
            )
            last_sent_status = current_status

        if knowledge.status in [KnowledgeStatus.COMPLETED, KnowledgeStatus.FAILED]:
            break

        await async_sleep(2)

        await db.refresh(knowledge)
