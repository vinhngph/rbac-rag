from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from uuid import UUID
from typing import List

from app.repositories.base import BaseRepository
from app.models.knowledge import Knowledge


class KnowledgeRepository(BaseRepository[Knowledge]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Knowledge, db)

    async def add_knowledge(self, knowledge: Knowledge) -> Knowledge:
        self.db.add(knowledge)
        return knowledge

    async def get_role_knowledges(self, role_id: UUID) -> List[Knowledge]:
        stm = select(Knowledge).where(Knowledge.role_id == role_id)
        return list((await self.db.exec(stm)).all())
