from fastapi import APIRouter, status, BackgroundTasks, UploadFile, File, HTTPException
from uuid import UUID
from typing import Annotated

from app.models.knowledge import KnowledgeRead
from app.db.session import DB_Session
from app.dependencies import CurrentUser, Allow
from app.services.zero_trust import zero_trust
from app.services.worker.knowledge import process_knowledge

router = APIRouter(
    prefix="/departments/{department_id}/knowledge", tags=["Knowledge Base"]
)


@router.post("/", response_model=KnowledgeRead, status_code=status.HTTP_201_CREATED)
async def upload_knowledge(
    department_id: UUID,
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    db: DB_Session,
    user: CurrentUser,
    _can_edit: Allow.EDIT,
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

    db.add(knowledge)
    await db.commit()
    await db.refresh(knowledge)

    background_tasks.add_task(process_knowledge, knowledge_id=knowledge.id)

    return knowledge
