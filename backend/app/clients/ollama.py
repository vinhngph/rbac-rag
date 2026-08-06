from ollama import AsyncClient

from app.core.config import settings

ollama_client = AsyncClient(
    host=settings.OLLAMA_HOST,
    headers={
        "Authorization": f"Bearer {settings.OLLAMA_API_KEY}"
        if settings.OLLAMA_API_KEY
        else None
    },
)
