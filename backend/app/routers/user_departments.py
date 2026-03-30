from fastapi import APIRouter, status, HTTPException
from typing import List
from sqlmodel import select, col
from uuid import UUID

from app.models.department import (
    Department,
    DepartmentRead,
    DepartmentCreate,
    DepartmentUpdate,
)
from app.models.role import Role
from app.models.permission import Permission
from app.models.links import UserDepartmentRoleLink, RolePermissionLink
from app.dependencies import CurrentUser, Allow
from app.db.session import DB_Session
from app.core.constants import PermissionName
from app.core.messages import ErrorMessages, SystemMessages

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=List[DepartmentRead])
async def get_departments(user: CurrentUser, db: DB_Session):
    stm = (
        select(Department)
        .join(UserDepartmentRoleLink)
        .where(UserDepartmentRoleLink.user_id == user.id, Department.status == True)
    )

    rs = await db.exec(statement=stm)
    user_departments = rs.all()

    return user_departments


@router.post("/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_new_department(
    user: CurrentUser,
    db: DB_Session,
    new_department: DepartmentCreate,
):
    # 1. Get permissions for admin role
    admin_permission_names = [p.value for p in PermissionName]
    stm = select(Permission).where(col(Permission.name).in_(admin_permission_names))
    rs = await db.exec(statement=stm)
    permissions = rs.all()

    if len(permissions) != len(admin_permission_names):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SystemMessages.DATABASE_SEED,
        )

    # 2. Create new Department
    department = Department.model_validate(new_department)
    db.add(department)

    # 3. Create new Role - "Admin" by creator
    admin_role = Role(name="Admin", department_id=department.id)
    db.add(admin_role)

    # 4. Add Department and Role to transaction
    await db.flush()

    # 5. Assign permissions for Role
    for perm in permissions:
        role_perm_link = RolePermissionLink(
            role_id=admin_role.id, permission_id=perm.id
        )
        db.add(role_perm_link)

    # 6. Link User - Department - Role
    link = UserDepartmentRoleLink(
        user_id=user.id, department_id=department.id, role_id=admin_role.id
    )
    db.add(link)

    # 7. Commit database
    await db.commit()
    await db.refresh(department)

    return department


@router.get("/{department_id}", response_model=DepartmentRead)
async def get_department(
    department_id: UUID,
    user: CurrentUser,
    db: DB_Session,
    _can_view: Allow.VIEW,
):
    department = await db.get(Department, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.DEPARTMENT_NOT_FOUND,
        )

    return department


@router.patch("/{department_id}", response_model=DepartmentRead)
async def update_department(
    department_id: UUID,
    update_data: DepartmentUpdate,
    user: CurrentUser,
    db: DB_Session,
    _can_edit: Allow.EDIT,
):
    department = await db.get(Department, department_id)

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.DEPARTMENT_NOT_FOUND,
        )

    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(department, key, value)

    db.add(department)
    await db.commit()
    await db.refresh(department)

    return department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: UUID, user: CurrentUser, db: DB_Session, _can_delete: Allow.DELETE
):
    department = await db.get(Department, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.DEPARTMENT_NOT_FOUND,
        )

    # Soft delete
    department.status = False

    db.add(department)
    await db.commit()

    return None
