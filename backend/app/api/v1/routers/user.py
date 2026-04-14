from fastapi import APIRouter

from app.models.user import UserRead
from app.api.dependencies import CurrentUser

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/metadata", response_model=UserRead)
async def metadata(user: CurrentUser):
    return user
