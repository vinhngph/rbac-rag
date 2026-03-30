from fastapi import APIRouter, Response, HTTPException, status
from sqlmodel import select

from app.models.user import User, UserLogin, UserRegister
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.db.session import DB_Session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(response: Response, login_data: UserLogin, db: DB_Session):
    statement = select(User).where(User.email == login_data.email)
    result = await db.exec(statement)
    user = result.one_or_none()

    if not user or not verify_password(
        login_data.plain_text_password, user.hashed_password
    ):
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
        max_age=int(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )

    return {"msg": "Login successfully"}


@router.post("/register")
async def register(response: Response, user_in: UserRegister, db: DB_Session):
    statement = select(User).where(User.email == user_in.email)
    result = await db.exec(statement)
    if result.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email registerd."
        )

    hashed_pw = get_password_hash((user_in.plain_text_password))

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
        max_age=int(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )

    return {"msg": "Register successfully"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=settings.JWT_AT_KEY)

    return {"msg": "Logged out"}
