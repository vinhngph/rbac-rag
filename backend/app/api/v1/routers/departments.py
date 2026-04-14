from fastapi import APIRouter, status
from typing import List
from uuid import UUID

from app.models.role import RootRoleRead, RootRoleCreate, RootRoleUpdate, RoleRead
from app.api.dependencies import CurrentUser, DB_Session
from app.services.role import RoleService

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=List[RootRoleRead])
async def get_departments(user: CurrentUser, db: DB_Session):
    """
    **List all joined departments of user**
    """
    role_service = RoleService(db)
    return await role_service.get_user_departments(user)


@router.post("/", response_model=RootRoleRead, status_code=status.HTTP_201_CREATED)
async def create_new_department(
    department_in: RootRoleCreate, user: CurrentUser, db: DB_Session
):
    role_service = RoleService(db)
    return await role_service.create_user_department(user, department_in)


@router.get("/{department_id}", response_model=List[RoleRead])
async def get_department(department_id: UUID, user: CurrentUser, db: DB_Session):
    """
    **Get tree roles (flat) of department - JSON list format**
    """
    role_service = RoleService(db)
    return await role_service.get_department(user, department_id)


@router.patch("/{department_id}", response_model=RootRoleRead)
async def update_department_name(
    department_id: UUID, update_data: RootRoleUpdate, user: CurrentUser, db: DB_Session
):
    role_service = RoleService(db)
    return await role_service.update_department(user, department_id, update_data)


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(department_id: UUID, user: CurrentUser, db: DB_Session):
    role_service = RoleService(db)
    return await role_service.delete_department(user, department_id)
