from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.modules.machines import service as machine_service
from app.modules.machines.schemas import MachineResponse

router = APIRouter()


@router.get("", response_model=List[MachineResponse], summary="List active manufacturing machines")
async def get_machines(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    return await machine_service.list_machines(db, active_only=active_only)
