from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.seed_db import seed_db
from app.routers import auth, user
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.PROJECT_NAME}...")

    async with AsyncSession(engine) as session:
        await seed_db(session)

    yield
    print("Shutting down...")


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

origins = [settings.FRONTEND_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}
