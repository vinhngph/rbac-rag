from fastapi import Depends
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_db

type DB_Session = Annotated[AsyncSession, Depends(get_db)]
