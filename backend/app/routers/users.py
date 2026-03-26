from fastapi import APIRouter, Depends
from typing import Annotated

from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]):
    return user
