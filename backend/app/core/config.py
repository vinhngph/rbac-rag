from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.types import NonEmptyString


class Settings(BaseSettings):
    DEBUG: bool = False
    PROJECT_NAME: NonEmptyString = "RBAC-RAG"

    # PostgreSQL
    DATABASE_URI: NonEmptyString

    # Qdrant
    QDRANT_SERVER: NonEmptyString
    QDRANT_COLLECTION: NonEmptyString
    QDRANT_API_KEY: str

    # Embed
    EMBEDDING_MODEL: NonEmptyString
    VECTOR_SIZE: int

    # OLLAMA
    OLLAMA_HOST: NonEmptyString
    OLLAMA_API_KEY: str

    LLM_MODEL: NonEmptyString

    # System
    JWT_AT_KEY: NonEmptyString
    JWT_SECRET_KEY: NonEmptyString
    JWT_ALGORITHM: NonEmptyString
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: float

    # Store service
    S3_BUCKET_NAME: NonEmptyString
    S3_ACCESS_KEY: NonEmptyString
    S3_SECRET_KEY: NonEmptyString
    S3_REGION: str = "auto"
    S3_ENDPOINT_URL: NonEmptyString

    # Front-end
    FRONTEND_ORIGIN: NonEmptyString

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    def __init__(self, **kwds: Any) -> None:
        super().__init__(**kwds)


settings = Settings()
