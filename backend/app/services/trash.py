from fastapi import Depends, HTTPException, status
from sqlmodel import select
from typing import Annotated

from app.dependencies.db_session import DB_Session
from app.core.messages import SystemMessages
from app.models.role import Role


class TrashService:
    def __init__(self, db: DB_Session) -> None:
        self.db = db

    async def get_trash_role(self) -> Role:
        stm = select(Role).where(Role.name == "Trash")
        trash = (await self.db.exec(stm)).one_or_none()

        if not trash:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=SystemMessages.DATABASE_SEED,
            )

        return trash

    async def move_role_to_trash(self, role: Role) -> None:
        trash = await self.get_trash_role()

        if role.id == trash.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Cannot remove."
            )

        role.original_parent_id = role.parent_id
        role.parent_id = trash.id

        self.db.add(role)
        await self.db.commit()


type UseTrashService = Annotated[TrashService, Depends(TrashService)]
