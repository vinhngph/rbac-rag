from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Document, PayloadSchemaType
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    PointStruct,
    VectorParams,
)

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
            await self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="knowledge_id",
                field_schema=PayloadSchemaType.KEYWORD,
            )

    async def store(self, points: list[PointStruct]) -> None:
        await self.client.upsert(collection_name=self.collection_name, points=points)

    async def search_context(
        self,
        query_vector: list[float] | Document,
        knowledge_ids: list[str],
        limit: int = 5,
    ) -> tuple[str, list[str]]:
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
