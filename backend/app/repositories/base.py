from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Generic, TypeVar, Type, Optional
from uuid import UUID

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get_by_id(self, obj_id: UUID) -> Optional[T]:
        stm = select(self.model).where(self.model.id == obj_id)  # type: ignore
        return (await self.db.exec(stm)).one_or_none()
