from fastapi import APIRouter

from app.routers import knowledge

router = APIRouter(prefix="/{role_id}", tags=["Role Organization"])

router.include_router(knowledge.router)
