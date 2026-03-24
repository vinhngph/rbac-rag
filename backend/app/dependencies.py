from fastapi import Request, HTTPException, status, Depends
from jwt import decode as jwt_decode, InvalidTokenError  # type: ignore
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.db.session import get_db
from app.orm_models.user import User

DB_Dependency = Annotated[AsyncSession, Depends(get_db)]


async def get_access_token_from_cookie(request: Request) -> str:
    """Get Access Token (access_token) from cookies"""

    ac_token = request.cookies.get(settings.JWT_AT_KEY)
    if not ac_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot find access_token from cookies.",
        )
    return ac_token


async def get_current_user(
    token: Annotated[str, Depends(get_access_token_from_cookie)],
    db: DB_Dependency,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
    )

    try:
        payload = jwt_decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("sub") is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    statement = select(User).where(User.id == payload.get("sub"))
    result = await db.exec(statement)
    user = result.one_or_none()

    if user is None:
        raise credentials_exception

    return user
