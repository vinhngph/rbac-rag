from fastapi import APIRouter, Depends
from typing import Annotated, List
from sqlmodel import select

from app.models.user import User
from app.models.department import DepartmentRead, Department
from app.models.links import UserDepartmentRoleLink
from app.dependencies import get_current_user, DB_Dependency

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=List[DepartmentRead])
async def get(user: Annotated[User, Depends(get_current_user)], db: DB_Dependency):
    stm = (
        select(Department)
        .join(UserDepartmentRoleLink)
        .where(UserDepartmentRoleLink.user_id == user.id)
    )

    rs = await db.exec(statement=stm)
    user_departments = rs.all()

    return user_departments
