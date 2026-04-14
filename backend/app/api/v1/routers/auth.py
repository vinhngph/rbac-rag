from fastapi import APIRouter, Response

from app.models.user import UserLogin, UserRegister
from app.core.config import settings
from app.api.dependencies import DB_Session
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(response: Response, login_data: UserLogin, db: DB_Session):
    auth_service = AuthService(db)

    access_token = await auth_service.login(login_data)

    response.set_cookie(
        key=settings.JWT_AT_KEY,
        value=access_token,
        httponly=True,
        secure=False if settings.DEBUG == "true" else True,
        samesite="lax",
        max_age=int(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )

    return {"msg": "Login successfully"}


@router.post("/register")
async def register(response: Response, user_in: UserRegister, db: DB_Session):
    auth_service = AuthService(db)

    access_token = await auth_service.register(user_in)

    response.set_cookie(
        key=settings.JWT_AT_KEY,
        value=access_token,
        httponly=True,
        secure=False if settings.DEBUG == "true" else True,
        samesite="lax",
        max_age=int(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )

    return {"msg": "Register successfully"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=settings.JWT_AT_KEY)

    return {"msg": "Logged out"}
