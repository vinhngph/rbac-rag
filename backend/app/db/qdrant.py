from qdrant_client import AsyncQdrantClient

from app.core.config import settings


def creat_qdrant_client() -> AsyncQdrantClient:
    if settings.QDRANT_API_KEY:
        return AsyncQdrantClient(
            url=settings.QDRANT_SERVER,
            api_key=settings.QDRANT_API_KEY,
            cloud_inference=True,
        )

    return AsyncQdrantClient(
        host=settings.QDRANT_SERVER,
        port=6334,
        prefer_grpc=True,
        check_compatibility=False,
    )


app_qdrant_client = creat_qdrant_client()
