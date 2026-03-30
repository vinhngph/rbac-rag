from sqlmodel import select, col

from app.db.session import DB_Session
from app.core.constants import PermissionName
from app.models.permission import Permission


async def seed_db(db: DB_Session):
    system_permissions = [p.value for p in PermissionName]

    stm = select(Permission).where(col(Permission.name).in_(system_permissions))
    rs = await db.exec(statement=stm)

    existing_permissions = [p.name for p in rs.all()]
    missing_permissions = [
        name for name in system_permissions if name not in existing_permissions
    ]

    if missing_permissions:
        for name in missing_permissions:
            db.add(Permission(name=name))

        await db.commit()
        print(f"[-] Seed permissions: {missing_permissions}")
