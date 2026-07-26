from sentence_transformers import SentenceTransformer

from app.core.config import settings


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return embedding_model.encode(chunks).tolist()  # type: ignore
