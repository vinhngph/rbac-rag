import httpx
from fastapi import HTTPException, status

from app.core.config import settings


async def verify_turnstile_token(token: str) -> bool:
    if not settings.TURNSTILE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Turnstile secret key is not configured",
        )

    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    data = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify Turnstile token",
            )

        result = response.json()
        return result.get("success", False)
