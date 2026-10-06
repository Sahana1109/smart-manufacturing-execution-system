from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.employees.models import Employee


async def list_employees(db: AsyncSession, active_only: bool = True) -> List[Employee]:
    stmt = select(Employee)
    if active_only:
        stmt = stmt.where(Employee.is_active.is_(True))
    stmt = stmt.order_by(Employee.employee_code.asc())
    res = await db.execute(stmt)
    return list(res.scalars().all())
