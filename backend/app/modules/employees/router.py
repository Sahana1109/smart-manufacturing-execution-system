import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user, require_roles
from app.modules.users.models import User
from app.modules.employees import service as employee_service
from app.modules.employees.schemas import (
    EmployeeResponse,
    EmployeeCreate,
    EmployeeUpdate,
)

router = APIRouter()


@router.get(
    "",
    response_model=List[EmployeeResponse],
    summary="List active or all manufacturing employees/operators"
)
async def get_employees(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lists manufacturing employees/operators. Accessible to all authenticated users.
    """
    return await employee_service.list_employees(db, active_only=active_only)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee/operator (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def create_employee(
    employee_in: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a new employee/operator entity. Requires ADMIN or PRODUCTION_MANAGER role.
    """
    return await employee_service.create_employee(db, employee_in, user_id=current_user.id)


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get employee details by ID"
)
async def get_employee(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetches employee details by ID. Accessible to all authenticated users.
    """
    return await employee_service.get_employee_by_id(db, employee_id)


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update employee details (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def update_employee(
    employee_id: uuid.UUID,
    employee_update: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates employee details. Requires ADMIN or PRODUCTION_MANAGER role.
    """
    return await employee_service.update_employee(db, employee_id, employee_update, user_id=current_user.id)


@router.delete(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Deactivate an employee/operator (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def delete_employee(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deactivates an employee entity (soft-delete). Requires ADMIN or PRODUCTION_MANAGER role.
    """
    return await employee_service.delete_employee(db, employee_id, user_id=current_user.id)
