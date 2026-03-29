from fastapi import APIRouter, Depends
from typing import Annotated, List
from sqlmodel import select

from app.models.user import User, UserRead
from app.models.department import DepartmentRead, Department
from app.models.links import UserDepartmentRoleLink
from app.dependencies import get_current_user, DB_Dependency

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/metadata", response_model=UserRead)
async def metadata(user: Annotated[User, Depends(get_current_user)]):
    return user


@router.get("/departments", response_model=List[DepartmentRead])
async def departments(
    user: Annotated[User, Depends(get_current_user)], db: DB_Dependency
):
    stm = (
        select(Department)
        .join(UserDepartmentRoleLink)
        .where(UserDepartmentRoleLink.user_id == user.id)
    )

    rs = await db.exec(statement=stm)
    user_departments = rs.all()

    return user_departments
