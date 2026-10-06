from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.machines.models import Machine


async def list_machines(db: AsyncSession, active_only: bool = True) -> List[Machine]:
    stmt = select(Machine)
    if active_only:
        stmt = stmt.where(Machine.is_active.is_(True))
    stmt = stmt.order_by(Machine.machine_code.asc())
    res = await db.execute(stmt)
    return list(res.scalars().all())
