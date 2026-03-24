from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.PROJECT_NAME}...")

    yield
    print("Shutting down...")


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}
