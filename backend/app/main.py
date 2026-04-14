from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.v1.routers import role
from app.api.v1.routers import auth, departments, knowledge
from app.core.exceptions.http_handler import http_exception_handler
from app.core.exceptions.app_exception import AppException
from app.core.config import settings
from app.core.seed_db import seed_db
from app.api.v1.routers import user
from app.db.session import engine
from app.services.zero_trust import ZeroTrust
from app.core.logger import logger_info


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger_info("System", f"Starting {settings.PROJECT_NAME}...")

    async with AsyncSession(engine) as session:
        await seed_db(session)

    zero_trust = ZeroTrust()

    await zero_trust.initialize()

    yield


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


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}
