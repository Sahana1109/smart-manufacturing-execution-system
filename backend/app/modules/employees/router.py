from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.modules.employees import service as employee_service
from app.modules.employees.schemas import EmployeeResponse

router = APIRouter()


@router.get("", response_model=List[EmployeeResponse], summary="List active manufacturing employees")
async def get_employees(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    return await employee_service.list_employees(db, active_only=active_only)
