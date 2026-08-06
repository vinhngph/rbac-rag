from ollama import AsyncClient
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Document

from app.core.config import settings


class EmbeddingService:
    def __init__(self, client: AsyncClient | AsyncQdrantClient) -> None:
        self.client = client
        self.embedding_model = settings.EMBEDDING_MODEL

    async def embed(self, content: str) -> list[float] | Document:
        if isinstance(self.client, AsyncClient):
            # Ollama Embed
            response = await self.client.embed(
                model=self.embedding_model, input=content
            )
            return list(response.embeddings[0])
        elif isinstance(self.client, AsyncQdrantClient):
            return Document(text=content, model=self.embedding_model)
        else:
            raise TypeError("Unsupported client type")
