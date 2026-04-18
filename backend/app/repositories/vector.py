from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance

from app.core.config import settings


class VectorRepository:
    def __init__(self, client: AsyncQdrantClient) -> None:
        self.client = client
        self.collection_name = settings.QDRANT_COLLECTION

    async def ensure_collection(self):
        exists = await self.client.collection_exists(self.collection_name)
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.VECTOR_SIZE, distance=Distance.COSINE
                ),
            )
