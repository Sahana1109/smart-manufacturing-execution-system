import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.modules.machines.models import Machine
from app.modules.machines.schemas import MachineCreate, MachineUpdate
from app.modules.audit_logs.service import log_audit_event


VALID_MACHINE_STATUSES = {"OPERATIONAL", "AVAILABLE", "IN_USE", "MAINTENANCE", "INACTIVE"}


async def list_machines(db: AsyncSession, active_only: bool = True) -> List[Machine]:
    """
    Lists manufacturing machines.
    """
    stmt = select(Machine)
    if active_only:
        stmt = stmt.where(Machine.is_active.is_(True))
    stmt = stmt.order_by(Machine.machine_code.asc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_machine_by_id(db: AsyncSession, machine_id: uuid.UUID) -> Machine:
    """
    Fetches machine entity by ID.
    """
    stmt = select(Machine).where(Machine.id == machine_id)
    res = await db.execute(stmt)
    machine = res.scalar_one_or_none()
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with ID '{machine_id}' not found"
        )
    return machine


async def create_machine(
    db: AsyncSession,
    machine_in: MachineCreate,
    user_id: Optional[uuid.UUID] = None
) -> Machine:
    """
    Creates a new machine entity.
    """
    # 1. Uniqueness check for machine_code
    stmt = select(Machine).where(Machine.machine_code == machine_in.machine_code.strip())
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Machine with code '{machine_in.machine_code}' already exists"
        )

    # 2. Status validation
    status_val = (machine_in.status or "OPERATIONAL").upper()
    if status_val not in VALID_MACHINE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid machine status '{status_val}'. Valid statuses: {sorted(list(VALID_MACHINE_STATUSES))}"
        )

    new_machine = Machine(
        machine_code=machine_in.machine_code.strip(),
        name=machine_in.name.strip(),
        status=status_val,
        is_active=machine_in.is_active if machine_in.is_active is not None else True
    )
    db.add(new_machine)
    await db.flush()

    if user_id:
        await log_audit_event(
            db,
            action="MACHINE_CREATED",
            entity_type="Machine",
            entity_id=str(new_machine.id),
            user_id=user_id,
            details={
                "machine_code": new_machine.machine_code,
                "name": new_machine.name,
                "status": new_machine.status
            }
        )

    await db.commit()
    await db.refresh(new_machine)
    return new_machine


async def update_machine(
    db: AsyncSession,
    machine_id: uuid.UUID,
    machine_update: MachineUpdate,
    user_id: Optional[uuid.UUID] = None
) -> Machine:
    """
    Updates existing machine properties.
    """
    machine = await get_machine_by_id(db, machine_id)

    if machine_update.machine_code is not None and machine_update.machine_code.strip() != machine.machine_code:
        stmt = select(Machine).where(
            Machine.machine_code == machine_update.machine_code.strip(),
            Machine.id != machine_id
        )
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Machine with code '{machine_update.machine_code}' already exists"
            )
        machine.machine_code = machine_update.machine_code.strip()

    if machine_update.name is not None:
        machine.name = machine_update.name.strip()

    if machine_update.status is not None:
        status_val = machine_update.status.upper()
        if status_val not in VALID_MACHINE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid machine status '{status_val}'. Valid statuses: {sorted(list(VALID_MACHINE_STATUSES))}"
            )
        machine.status = status_val

    if machine_update.is_active is not None:
        machine.is_active = machine_update.is_active

    if user_id:
        await log_audit_event(
            db,
            action="MACHINE_UPDATED",
            entity_type="Machine",
            entity_id=str(machine.id),
            user_id=user_id,
            details={
                "machine_code": machine.machine_code,
                "name": machine.name,
                "status": machine.status,
                "is_active": machine.is_active
            }
        )

    await db.commit()
    await db.refresh(machine)
    return machine


async def change_machine_status(
    db: AsyncSession,
    machine_id: uuid.UUID,
    new_status: str,
    user_id: Optional[uuid.UUID] = None
) -> Machine:
    """
    Changes machine operational status (e.g. OPERATIONAL, MAINTENANCE, IN_USE, INACTIVE).
    """
    machine = await get_machine_by_id(db, machine_id)
    status_val = new_status.upper()
    if status_val not in VALID_MACHINE_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid machine status '{status_val}'. Valid statuses: {sorted(list(VALID_MACHINE_STATUSES))}"
        )

    old_status = machine.status
    machine.status = status_val

    if user_id:
        await log_audit_event(
            db,
            action="MACHINE_STATUS_CHANGED",
            entity_type="Machine",
            entity_id=str(machine.id),
            user_id=user_id,
            details={
                "old_status": old_status,
                "new_status": status_val,
                "machine_code": machine.machine_code
            }
        )

    await db.commit()
    await db.refresh(machine)
    return machine


async def delete_machine(
    db: AsyncSession,
    machine_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None
) -> Machine:
    """
    Soft-deletes / deactivates a machine entity.
    """
    machine = await get_machine_by_id(db, machine_id)
    machine.is_active = False
    machine.status = "INACTIVE"

    if user_id:
        await log_audit_event(
            db,
            action="MACHINE_DEACTIVATED",
            entity_type="Machine",
            entity_id=str(machine.id),
            user_id=user_id,
            details={"machine_code": machine.machine_code}
        )

    await db.commit()
    await db.refresh(machine)
    return machine
