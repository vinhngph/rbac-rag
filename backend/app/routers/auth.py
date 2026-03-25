from fastapi import APIRouter, Response, HTTPException, status
from sqlmodel import select

from app.http_models.auth import LoginRequest
from app.orm_models.user import User, UserCreate
from app.core.security import verify_password, create_access_token, get_password_hash
from app.dependencies import DB_Dependency
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(response: Response, login_data: LoginRequest, db: DB_Dependency):
    statement = select(User).where(User.email == login_data.email)
    result = await db.exec(statement)
    user = result.one_or_none()

    if not user or verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    access_token = create_access_token(user)

    response.set_cookie(
        key=settings.JWT_AT_KEY,
        value=access_token,
        httponly=True,
        secure=False if settings.DEBUG == "true" else True,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"msg": "Login successfully"}


@router.post("/register")
async def register(response: Response, user_in: UserCreate, db: DB_Dependency):
    statement = select(User).where(User.email == user_in.email)
    result = await db.exec(statement)
    if result.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email registerd."
        )

    hashed_pw = get_password_hash((user_in.password))

    new_user = User(email=user_in.email, name=user_in.name, hashed_password=hashed_pw)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(new_user)

    response.set_cookie(
        key=settings.JWT_AT_KEY,
        value=access_token,
        httponly=True,
        secure=False if settings.DEBUG == "true" else True,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"msg": "Register successfully"}
