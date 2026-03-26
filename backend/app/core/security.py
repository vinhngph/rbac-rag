from jwt import encode as jwt_encode  # type: ignore
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.user import User, UserAT

password_hash = PasswordHash.recommended()


def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_text_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = UserAT(sub=user.id, exp=expire).model_dump(mode="json")

    return jwt_encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
