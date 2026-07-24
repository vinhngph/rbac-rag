from asyncio import CancelledError
from asyncio import create_task as async_create_task
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.routers import auth, chat, departments, knowledge, role, user
from app.core.config import settings
from app.core.exceptions.app_exception import AppException
from app.core.exceptions.http_handler import http_exception_handler
from app.core.logger import logger_error, logger_info
from app.core.seed_db import seed_db
from app.db.qdrant import app_qdrant_client
from app.db.session import engine
from app.repositories.vector import VectorRepository
from app.services.worker.knowledge import knowledge_worker_daemon
from app.services.zero_trust import ZeroTrust


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger_info("System", f"Starting {settings.PROJECT_NAME}...")
    daemon_task = async_create_task(knowledge_worker_daemon())

    async with AsyncSession(engine) as session:
        await seed_db(session)

    zero_trust = ZeroTrust()
    await zero_trust.initialize()

    try:
        logger_info("System", f"Connecting {settings.QDRANT_COLLECTION}")

        vector_repo = VectorRepository(app_qdrant_client)
        await vector_repo.ensure_collection()
        logger_info("System", f"{settings.QDRANT_COLLECTION} ready.")
    except Exception as e:
        logger_error(
            "System", f"Failed to connect {settings.QDRANT_COLLECTION}: {str(e)}"
        )

    yield

    daemon_task.cancel()

    try:
        await daemon_task
    except CancelledError:
        pass


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

origins = [settings.FRONTEND_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, http_exception_handler)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(departments.router)
app.include_router(role.router)
app.include_router(knowledge.router)
app.include_router(chat.router)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}
