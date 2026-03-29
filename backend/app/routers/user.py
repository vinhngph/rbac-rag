from fastapi import APIRouter, Depends
from typing import Annotated

from app.routers.user_departments import router as user_departments_router
from app.models.user import User, UserRead
from app.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/metadata", response_model=UserRead)
async def metadata(user: Annotated[User, Depends(get_current_user)]):
    return user


router.include_router(user_departments_router)
