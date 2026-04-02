from fastapi import APIRouter

from app.routers import user_departments, knowledge
from app.models.user import UserRead
from app.dependencies import CurrentUser

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/metadata", response_model=UserRead)
async def metadata(user: CurrentUser):
    return user


router.include_router(user_departments.router)
router.include_router(knowledge.router)
