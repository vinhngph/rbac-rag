from sqlmodel.ext.asyncio.session import AsyncSession
from functools import cached_property

from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.exceptions.app_exception import AppException
from app.repositories.user import UserRepository
from app.models.user import UserLogin, UserRegister, User


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @cached_property
    def user_repo(self) -> UserRepository:
        return UserRepository(self.db)

    async def login(self, login_data: UserLogin) -> str:
        user = await self.user_repo.get_user_by_email(login_data.email)

        if not user or not verify_password(
            login_data.plain_text_password, user.hashed_password
        ):
            raise AppException(401, "Invalid email or password")

        return create_access_token(user)

    async def register(self, user_in: UserRegister) -> str:
        user = await self.user_repo.get_user_by_email(user_in.email)

        if user:
            raise AppException(400, "Email registerd.")

        hashed_pw = get_password_hash(user_in.plain_text_password)
        new_user = User(
            email=user_in.email, name=user_in.name, hashed_password=hashed_pw
        )

        self.user_repo.create(new_user)

        await self.db.commit()
        await self.db.refresh(new_user)

        access_token = create_access_token(new_user)

        return access_token
