from sqlmodel import select, col

from app.db.session import DB_Session
from app.core.constants import PermissionName
from app.models.permission import Permission
from app.core.logger import logger_info


async def seed_db(db: DB_Session):
    system_permissions = [p.value for p in PermissionName]

    stm = select(Permission.name).where(col(Permission.name).in_(system_permissions))

    existing_permissions = (await db.exec(statement=stm)).all()

    missing_permissions = [
        name for name in system_permissions if name not in existing_permissions
    ]

    if missing_permissions:
        for name in missing_permissions:
            db.add(Permission(name=PermissionName(name)))

        await db.commit()
        logger_info("Database", f"Seed {missing_permissions}.")
