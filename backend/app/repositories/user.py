from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from app.repositories.base import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        stm = select(User).where(User.email == email)
        return (await self.db.exec(stm)).one_or_none()

    def create(self, user: User) -> User:
        self.db.add(user)
        return user
