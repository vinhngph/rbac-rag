from typing import List

from sentence_transformers import SentenceTransformer

from app.core.config import settings


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return embedding_model.encode(chunks).tolist()  # type: ignore
