from uuid import UUID
from asyncio import sleep as async_sleep

from app.db.session import AsyncSessionLocal
from app.models.knowledge import Knowledge
from app.core.constants import KnowledgeStatus


async def process_knowledge(knowledge_id: UUID):
    """
    RAG processing
    """

    async with AsyncSessionLocal() as db:
        knowledge = await db.get(Knowledge, knowledge_id)
        if not knowledge:
            return
        try:
            knowledge.status = KnowledgeStatus.EXTRACTING
            await db.commit()
            await async_sleep(2)  # Simulation

            knowledge.status = KnowledgeStatus.CHUNKING
            await db.commit()
            await async_sleep(2)  # Simulation

            knowledge.status = KnowledgeStatus.EMBEDDING
            await db.commit()
            await async_sleep(2)  # Simulation

            knowledge.status = KnowledgeStatus.COMPLETED
            await db.commit()
        except Exception:
            knowledge.status = KnowledgeStatus.FAILED
            await db.commit()
