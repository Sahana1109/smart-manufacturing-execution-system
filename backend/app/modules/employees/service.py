import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.modules.employees.models import Employee
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate
from app.modules.audit_logs.service import log_audit_event


async def list_employees(db: AsyncSession, active_only: bool = True) -> List[Employee]:
    """
    Lists manufacturing employees/operators.
    """
    stmt = select(Employee)
    if active_only:
        stmt = stmt.where(Employee.is_active.is_(True))
    stmt = stmt.order_by(Employee.employee_code.asc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_employee_by_id(db: AsyncSession, employee_id: uuid.UUID) -> Employee:
    """
    Fetches employee entity by ID.
    """
    stmt = select(Employee).where(Employee.id == employee_id)
    res = await db.execute(stmt)
    emp = res.scalar_one_or_none()
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID '{employee_id}' not found"
        )
    return emp


async def create_employee(
    db: AsyncSession,
    employee_in: EmployeeCreate,
    user_id: Optional[uuid.UUID] = None
) -> Employee:
    """
    Creates a new employee/operator entity.
    """
    # 1. Uniqueness check for employee_code
    stmt = select(Employee).where(Employee.employee_code == employee_in.employee_code.strip())
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with code '{employee_in.employee_code}' already exists"
        )

    new_emp = Employee(
        employee_code=employee_in.employee_code.strip(),
        first_name=employee_in.first_name.strip(),
        last_name=employee_in.last_name.strip(),
        role_title=employee_in.role_title.strip() if employee_in.role_title else None,
        is_active=employee_in.is_active if employee_in.is_active is not None else True
    )
    db.add(new_emp)
    await db.flush()

    if user_id:
        await log_audit_event(
            db,
            action="EMPLOYEE_CREATED",
            entity_type="Employee",
            entity_id=str(new_emp.id),
            user_id=user_id,
            details={
                "employee_code": new_emp.employee_code,
                "name": f"{new_emp.first_name} {new_emp.last_name}",
                "role_title": new_emp.role_title
            }
        )

    await db.commit()
    await db.refresh(new_emp)
    return new_emp


async def update_employee(
    db: AsyncSession,
    employee_id: uuid.UUID,
    employee_update: EmployeeUpdate,
    user_id: Optional[uuid.UUID] = None
) -> Employee:
    """
    Updates existing employee entity details.
    """
    emp = await get_employee_by_id(db, employee_id)

    if employee_update.employee_code is not None and employee_update.employee_code.strip() != emp.employee_code:
        stmt = select(Employee).where(
            Employee.employee_code == employee_update.employee_code.strip(),
            Employee.id != employee_id
        )
        res = await db.execute(stmt)
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with code '{employee_update.employee_code}' already exists"
            )
        emp.employee_code = employee_update.employee_code.strip()

    if employee_update.first_name is not None:
        emp.first_name = employee_update.first_name.strip()
    if employee_update.last_name is not None:
        emp.last_name = employee_update.last_name.strip()
    if employee_update.role_title is not None:
        emp.role_title = employee_update.role_title.strip() if employee_update.role_title else None
    if employee_update.is_active is not None:
        emp.is_active = employee_update.is_active

    if user_id:
        await log_audit_event(
            db,
            action="EMPLOYEE_UPDATED",
            entity_type="Employee",
            entity_id=str(emp.id),
            user_id=user_id,
            details={
                "employee_code": emp.employee_code,
                "name": f"{emp.first_name} {emp.last_name}",
                "role_title": emp.role_title,
                "is_active": emp.is_active
            }
        )

    await db.commit()
    await db.refresh(emp)
    return emp


async def delete_employee(
    db: AsyncSession,
    employee_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None
) -> Employee:
    """
    Deactivates an employee/operator entity (soft-delete).
    """
    emp = await get_employee_by_id(db, employee_id)
    emp.is_active = False

    if user_id:
        await log_audit_event(
            db,
            action="EMPLOYEE_DEACTIVATED",
            entity_type="Employee",
            entity_id=str(emp.id),
            user_id=user_id,
            details={"employee_code": emp.employee_code}
        )

    await db.commit()
    await db.refresh(emp)
    return emp
