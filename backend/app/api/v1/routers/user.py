from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.models.user import UserRead

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/metadata", response_model=UserRead)
async def metadata(user: CurrentUser):
    return user
