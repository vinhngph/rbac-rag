from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchAny,
)

from typing import List, Tuple

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

    async def search_context(
        self, query_vector: List[float], knowledge_ids: List[str], limit: int = 5
    ) -> Tuple[str, List[str]]:
        result = (
            await self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="knowledge_id", match=MatchAny(any=knowledge_ids)
                        )
                    ]
                ),
                limit=limit,
                score_threshold=0.5,
            )
        ).points

        contexts = [hit.payload.get("text", "") for hit in result if hit.payload]
        res_knowledge_ids = {
            hit.payload.get("knowledge_id", "") for hit in result if hit.payload
        }

        return "\n\n---\n\n".join(contexts), list(res_knowledge_ids)
