import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user, require_roles
from app.modules.users.models import User
from app.modules.machines import service as machine_service
from app.modules.machines.schemas import (
    MachineResponse,
    MachineCreate,
    MachineUpdate,
    MachineStatusUpdate,
)

router = APIRouter()


@router.get(
    "",
    response_model=List[MachineResponse],
    summary="List active or all manufacturing machines"
)
async def get_machines(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lists manufacturing machines. Accessible to all authenticated users.
    """
    return await machine_service.list_machines(db, active_only=active_only)


@router.post(
    "",
    response_model=MachineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new machine (Admin / Production Manager / Supervisor)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"))]
)
async def create_machine(
    machine_in: MachineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a new machine entity. Requires ADMIN, PRODUCTION_MANAGER, or SUPERVISOR role.
    """
    return await machine_service.create_machine(db, machine_in, user_id=current_user.id)


@router.get(
    "/{machine_id}",
    response_model=MachineResponse,
    summary="Get machine details by ID"
)
async def get_machine(
    machine_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetches machine entity details by ID. Accessible to all authenticated users.
    """
    return await machine_service.get_machine_by_id(db, machine_id)


@router.put(
    "/{machine_id}",
    response_model=MachineResponse,
    summary="Update machine details (Admin / Production Manager / Supervisor)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"))]
)
async def update_machine(
    machine_id: uuid.UUID,
    machine_update: MachineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates machine details. Requires ADMIN, PRODUCTION_MANAGER, or SUPERVISOR role.
    """
    return await machine_service.update_machine(db, machine_id, machine_update, user_id=current_user.id)


@router.patch(
    "/{machine_id}/status",
    response_model=MachineResponse,
    summary="Update machine operational status (Admin / Production Manager / Supervisor)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"))]
)
async def update_machine_status(
    machine_id: uuid.UUID,
    status_update: MachineStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates machine status (e.g. OPERATIONAL, MAINTENANCE, IN_USE, INACTIVE).
    """
    return await machine_service.change_machine_status(
        db, machine_id, status_update.status, user_id=current_user.id
    )


@router.delete(
    "/{machine_id}",
    response_model=MachineResponse,
    summary="Deactivate a machine (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def delete_machine(
    machine_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deactivates a machine entity (soft-delete). Requires ADMIN or PRODUCTION_MANAGER role.
    """
    return await machine_service.delete_machine(db, machine_id, user_id=current_user.id)
