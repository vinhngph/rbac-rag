from fastapi import Request, HTTPException, status, Depends
from jwt import decode as jwt_decode, InvalidTokenError  # type: ignore
from typing import Annotated, List
from sqlmodel import select, col
from uuid import UUID

from app.core.config import settings
from app.core.constants import PermissionName
from app.db.session import DB_Session
from app.models.user import User
from app.models.permission import Permission
from app.models.role import Role
from app.models.links import RolePermissionLink, UserDepartmentRoleLink


def get_access_token_from_cookie(request: Request) -> str:
    """Get Access Token (access_token) from cookies"""

    ac_token = request.cookies.get(settings.JWT_AT_KEY)
    if not ac_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot find access_token from cookies.",
        )
    return ac_token


async def get_current_user(
    token: Annotated[str, Depends(get_access_token_from_cookie)],
    db: DB_Session,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
    )

    try:
        payload = jwt_decode(
            token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("sub") is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    statement = select(User).where(User.id == payload.get("sub"))
    result = await db.exec(statement)
    user = result.one_or_none()

    if user is None:
        raise credentials_exception

    return user


type CurrentUser = Annotated[User, Depends(get_current_user)]


class RequirePermissions:
    def __init__(
        self, required_permissions: List[PermissionName], require_all: bool = True
    ) -> None:
        self.required_permissions = [p.value for p in required_permissions]
        self.require_all = require_all

    async def __call__(self, department_id: UUID, user: CurrentUser, db: DB_Session):
        stm = (
            select(Permission.name)
            .join(RolePermissionLink)
            .join(Role)
            .join(UserDepartmentRoleLink)
            .where(
                UserDepartmentRoleLink.user_id == user.id,
                UserDepartmentRoleLink.department_id == department_id,
                col(Permission.name).in_(self.required_permissions),
            )
        )
        rs = await db.exec(statement=stm)
        founded_permission = rs.all()

        # LOGIC AND
        if self.require_all:
            if len(set(founded_permission)) != len(set(self.required_permissions)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. You need ALL of these permissions: {self.required_permissions}",
                )

        # LOGIC OR
        else:
            if len(founded_permission) == 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. You need AT LEAST ONE of these permissions: {self.required_permissions}",
                )

        return True


class Allow:
    """
    Permissions allow
    """

    EDIT = Annotated[bool, Depends(RequirePermissions([PermissionName.EDIT]))]
    VIEW = Annotated[bool, Depends(RequirePermissions([PermissionName.VIEW]))]
    DELETE = Annotated[bool, Depends(RequirePermissions([PermissionName.DELETE]))]
