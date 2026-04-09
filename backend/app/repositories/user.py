from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        stm = select(User).where(User.email == email)
        return (await self.db.exec(stm)).one_or_none()
