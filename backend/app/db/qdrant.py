from qdrant_client import AsyncQdrantClient

from app.core.config import settings

app_qdrant_client = AsyncQdrantClient(
    host=settings.QDRANT_SERVER, port=6334, prefer_grpc=True, check_compatibility=False
)
