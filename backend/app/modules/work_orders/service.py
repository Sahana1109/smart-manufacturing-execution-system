import uuid
import math
from typing import List, Optional, Tuple
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.work_orders.models import WorkOrder, WorkOrderStatus, WorkOrderPriority
from app.modules.production_planning.models import ProductionPlan
from app.modules.products.models import Product
from app.modules.machines.models import Machine
from app.modules.employees.models import Employee
from app.modules.work_orders.schemas import WorkOrderCreate, WorkOrderUpdate, WorkOrderAssignRequest
from app.modules.audit_logs.service import log_audit_event

ALLOWED_WO_STATUS_TRANSITIONS = {
    WorkOrderStatus.DRAFT: [WorkOrderStatus.RELEASED, WorkOrderStatus.CANCELLED],
    WorkOrderStatus.RELEASED: [WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.CANCELLED],
    WorkOrderStatus.IN_PROGRESS: [WorkOrderStatus.PAUSED, WorkOrderStatus.COMPLETED, WorkOrderStatus.CANCELLED],
    WorkOrderStatus.PAUSED: [WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.CANCELLED],
    WorkOrderStatus.COMPLETED: [WorkOrderStatus.CLOSED],
    WorkOrderStatus.CLOSED: [],
    WorkOrderStatus.CANCELLED: [],
}


async def generate_work_order_number(db: AsyncSession) -> str:
    """
    Generates next sequential work order number in format WO-YYYY-XXXX.
    """
    current_year = datetime.now().year
    prefix = f"WO-{current_year}-"
    
    stmt = select(func.count(WorkOrder.id)).where(WorkOrder.work_order_number.like(f"{prefix}%"))
    res = await db.execute(stmt)
    count = res.scalar() or 0
    
    return f"{prefix}{count + 1:04d}"


async def create_work_order(
    db: AsyncSession,
    order_in: WorkOrderCreate,
    user_id: uuid.UUID
) -> WorkOrder:
    """
    Creates a new work order with production plan validation and audit logging.
    """
    # 1. Quantity validation
    if order_in.planned_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="planned_quantity must be greater than 0"
        )

    # 2. Date range validation
    if order_in.start_date > order_in.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be after due_date"
        )

    # 3. Production Plan existence validation
    plan_stmt = select(ProductionPlan).where(ProductionPlan.id == order_in.production_plan_id)
    plan_res = await db.execute(plan_stmt)
    plan = plan_res.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production Plan with ID '{order_in.production_plan_id}' not found"
        )

    # 4. Product existence & active status validation
    prod_stmt = select(Product).where(Product.id == order_in.product_id)
    prod_res = await db.execute(prod_stmt)
    product = prod_res.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{order_in.product_id}' not found"
        )
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot create work order for inactive product '{product.name}'"
        )

    # 5. Machine & Employee active checks if assigned
    if order_in.assigned_machine_id:
        m_stmt = select(Machine).where(Machine.id == order_in.assigned_machine_id)
        m_res = await db.execute(m_stmt)
        machine = m_res.scalar_one_or_none()
        if not machine or not machine.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned machine does not exist or is inactive"
            )

    if order_in.assigned_employee_id:
        e_stmt = select(Employee).where(Employee.id == order_in.assigned_employee_id)
        e_res = await db.execute(e_stmt)
        emp = e_res.scalar_one_or_none()
        if not emp or not emp.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned employee does not exist or is inactive"
            )

    # 6. Work Order number resolution & uniqueness
    wo_number = order_in.work_order_number.strip() if order_in.work_order_number else await generate_work_order_number(db)
    
    num_stmt = select(WorkOrder).where(WorkOrder.work_order_number == wo_number)
    num_res = await db.execute(num_stmt)
    if num_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Work Order number '{wo_number}' already exists"
        )

    # 7. Create Entity
    new_order = WorkOrder(
        work_order_number=wo_number,
        production_plan_id=order_in.production_plan_id,
        product_id=order_in.product_id,
        planned_quantity=order_in.planned_quantity,
        start_date=order_in.start_date,
        due_date=order_in.due_date,
        priority=order_in.priority,
        status=WorkOrderStatus.DRAFT,
        notes=order_in.notes,
        created_by_id=user_id,
        assigned_machine_id=order_in.assigned_machine_id,
        assigned_employee_id=order_in.assigned_employee_id,
    )
    db.add(new_order)
    await db.flush()

    # 8. Record Audit Event
    await log_audit_event(
        db,
        action="WORK_ORDER_CREATED",
        entity_type="WorkOrder",
        entity_id=str(new_order.id),
        user_id=user_id,
        details={
            "work_order_number": new_order.work_order_number,
            "production_plan_id": str(new_order.production_plan_id),
            "product_code": product.product_code,
            "planned_quantity": new_order.planned_quantity,
            "status": new_order.status.value,
        }
    )

    await db.commit()
    return await get_work_order_by_id(db, new_order.id)  # type: ignore


async def get_work_order_by_id(db: AsyncSession, order_id: uuid.UUID) -> WorkOrder:
    """
    Fetches work order by ID with relationships pre-loaded.
    """
    stmt = (
        select(WorkOrder)
        .where(WorkOrder.id == order_id)
        .options(
            selectinload(WorkOrder.product),
            selectinload(WorkOrder.production_plan),
            selectinload(WorkOrder.created_by),
            selectinload(WorkOrder.assigned_machine),
            selectinload(WorkOrder.assigned_employee)
        )
    )
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID '{order_id}' not found"
        )
    return order


async def list_work_orders(
    db: AsyncSession,
    status_filter: Optional[WorkOrderStatus] = None,
    priority_filter: Optional[WorkOrderPriority] = None,
    plan_id_filter: Optional[uuid.UUID] = None,
    product_id_filter: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> Tuple[List[WorkOrder], int, int]:
    """
    Lists work orders matching filter criteria.
    Returns (items, total_count, total_pages).
    """
    stmt = select(WorkOrder).options(
        selectinload(WorkOrder.product),
        selectinload(WorkOrder.production_plan),
        selectinload(WorkOrder.created_by),
        selectinload(WorkOrder.assigned_machine),
        selectinload(WorkOrder.assigned_employee)
    )
    
    conditions = []
    if status_filter:
        conditions.append(WorkOrder.status == status_filter)
    if priority_filter:
        conditions.append(WorkOrder.priority == priority_filter)
    if plan_id_filter:
        conditions.append(WorkOrder.production_plan_id == plan_id_filter)
    if product_id_filter:
        conditions.append(WorkOrder.product_id == product_id_filter)
    if search:
        search_term = f"%{search.strip()}%"
        stmt = stmt.join(WorkOrder.product)
        conditions.append(
            or_(
                WorkOrder.work_order_number.ilike(search_term),
                Product.product_code.ilike(search_term),
                Product.name.ilike(search_term)
            )
        )

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Count Query
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    pages = math.ceil(total / limit) if total > 0 else 1
    offset = (page - 1) * limit

    # Execute Paginated Query
    stmt = stmt.order_by(WorkOrder.created_at.desc()).offset(offset).limit(limit)
    res = await db.execute(stmt)
    items = list(res.scalars().all())

    return items, total, pages


async def update_work_order(
    db: AsyncSession,
    order_id: uuid.UUID,
    order_update: WorkOrderUpdate,
    user_id: uuid.UUID
) -> WorkOrder:
    """
    Updates work order parameters.
    """
    order = await get_work_order_by_id(db, order_id)

    if order.status in (WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED, WorkOrderStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update a work order that is already {order.status.value}"
        )

    start_d = order_update.start_date or order.start_date
    due_d = order_update.due_date or order.due_date
    if start_d > due_d:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be after due_date"
        )

    updated_fields = {}
    if order_update.planned_quantity is not None:
        order.planned_quantity = order_update.planned_quantity
        updated_fields["planned_quantity"] = order_update.planned_quantity
    if order_update.start_date is not None:
        order.start_date = order_update.start_date
        updated_fields["start_date"] = str(order_update.start_date)
    if order_update.due_date is not None:
        order.due_date = order_update.due_date
        updated_fields["due_date"] = str(order_update.due_date)
    if order_update.priority is not None:
        order.priority = order_update.priority
        updated_fields["priority"] = order_update.priority.value
    if order_update.notes is not None:
        order.notes = order_update.notes
        updated_fields["notes"] = order_update.notes

    if updated_fields:
        await log_audit_event(
            db,
            action="WORK_ORDER_UPDATED",
            entity_type="WorkOrder",
            entity_id=str(order.id),
            user_id=user_id,
            details=updated_fields
        )

    await db.commit()
    return await get_work_order_by_id(db, order.id)  # type: ignore


async def change_work_order_status(
    db: AsyncSession,
    order_id: uuid.UUID,
    target_status: WorkOrderStatus,
    user_id: uuid.UUID,
    user_roles: Optional[List[str]] = None
) -> WorkOrder:
    """
    Executes controlled status transitions for Work Order state machine.
    """
    order = await get_work_order_by_id(db, order_id)
    current_status = order.status

    if target_status == current_status:
        return order

    # RBAC Enforcement: Operators are restricted to execution-only status transitions
    if user_roles and "OPERATOR" in user_roles:
        management_roles = {"ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"}
        if not any(r in management_roles for r in user_roles):
            execution_statuses = {WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.PAUSED, WorkOrderStatus.COMPLETED}
            if target_status not in execution_statuses:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Operators can only transition execution statuses ({', '.join([s.value for s in execution_statuses])})"
                )

    allowed_next = ALLOWED_WO_STATUS_TRANSITIONS.get(current_status, [])
    if target_status not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status.value}' to '{target_status.value}'. Allowed transitions: {[s.value for s in allowed_next]}"
        )

    order.status = target_status

    # Auto-synchronize assigned machine status during execution transitions
    if order.assigned_machine_id:
        m_stmt = select(Machine).where(Machine.id == order.assigned_machine_id)
        m_res = await db.execute(m_stmt)
        machine = m_res.scalar_one_or_none()
        if machine and machine.status != "MAINTENANCE" and machine.status != "INACTIVE":
            if target_status == WorkOrderStatus.IN_PROGRESS:
                machine.status = "IN_USE"
            elif target_status in (WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED, WorkOrderStatus.CANCELLED, WorkOrderStatus.PAUSED):
                if machine.status == "IN_USE":
                    machine.status = "OPERATIONAL"

    await log_audit_event(
        db,
        action="WORK_ORDER_STATUS_CHANGED",
        entity_type="WorkOrder",
        entity_id=str(order.id),
        user_id=user_id,
        details={
            "from_status": current_status.value,
            "to_status": target_status.value,
        }
    )

    await db.commit()
    return await get_work_order_by_id(db, order.id)  # type: ignore


async def assign_work_order(
    db: AsyncSession,
    order_id: uuid.UUID,
    assign_in: WorkOrderAssignRequest,
    user_id: uuid.UUID
) -> WorkOrder:
    """
    Assigns machine and/or employee to a work order.
    """
    order = await get_work_order_by_id(db, order_id)

    if order.status in (WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED, WorkOrderStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot assign resources to a work order in '{order.status.value}' state"
        )

    if assign_in.assigned_machine_id is not None:
        m_stmt = select(Machine).where(Machine.id == assign_in.assigned_machine_id)
        m_res = await db.execute(m_stmt)
        m = m_res.scalar_one_or_none()
        if not m or not m.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned machine does not exist or is inactive"
            )
        if m.status in ("MAINTENANCE", "INACTIVE"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot assign machine '{m.machine_code}' in {m.status} status"
            )

        order.assigned_machine_id = assign_in.assigned_machine_id

        # If WO is currently IN_PROGRESS, set machine to IN_USE
        if order.status == WorkOrderStatus.IN_PROGRESS:
            m.status = "IN_USE"

        await log_audit_event(
            db,
            action="WORK_ORDER_MACHINE_ASSIGNED",
            entity_type="WorkOrder",
            entity_id=str(order.id),
            user_id=user_id,
            details={"machine_code": m.machine_code, "machine_name": m.name}
        )

    if assign_in.assigned_employee_id is not None:
        e_stmt = select(Employee).where(Employee.id == assign_in.assigned_employee_id)
        e_res = await db.execute(e_stmt)
        emp = e_res.scalar_one_or_none()
        if not emp or not emp.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned employee does not exist or is inactive"
            )
        order.assigned_employee_id = assign_in.assigned_employee_id
        await log_audit_event(
            db,
            action="WORK_ORDER_EMPLOYEE_ASSIGNED",
            entity_type="WorkOrder",
            entity_id=str(order.id),
            user_id=user_id,
            details={"employee_code": emp.employee_code, "employee_name": f"{emp.first_name} {emp.last_name}"}
        )

    await db.commit()
    return await get_work_order_by_id(db, order.id)  # type: ignore


async def unassign_work_order_resource(
    db: AsyncSession,
    order_id: uuid.UUID,
    unassign_machine: bool = False,
    unassign_employee: bool = False,
    user_id: Optional[uuid.UUID] = None
) -> WorkOrder:
    """
    Unassigns machine and/or employee from a work order.
    """
    order = await get_work_order_by_id(db, order_id)

    if order.status in (WorkOrderStatus.COMPLETED, WorkOrderStatus.CLOSED, WorkOrderStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot modify assignments for a work order in '{order.status.value}' state"
        )

    if unassign_machine and order.assigned_machine_id:
        if order.assigned_machine and order.assigned_machine.status == "IN_USE":
            order.assigned_machine.status = "OPERATIONAL"
        order.assigned_machine_id = None
        if user_id:
            await log_audit_event(
                db,
                action="WORK_ORDER_MACHINE_UNASSIGNED",
                entity_type="WorkOrder",
                entity_id=str(order.id),
                user_id=user_id,
                details={"work_order_number": order.work_order_number}
            )

    if unassign_employee and order.assigned_employee_id:
        order.assigned_employee_id = None
        if user_id:
            await log_audit_event(
                db,
                action="WORK_ORDER_EMPLOYEE_UNASSIGNED",
                entity_type="WorkOrder",
                entity_id=str(order.id),
                user_id=user_id,
                details={"work_order_number": order.work_order_number}
            )

    await db.commit()
    return await get_work_order_by_id(db, order.id)  # type: ignore


async def cancel_work_order(
    db: AsyncSession,
    order_id: uuid.UUID,
    user_id: uuid.UUID
) -> WorkOrder:
    """
    Cancels an existing active work order.
    """
    return await change_work_order_status(db, order_id, WorkOrderStatus.CANCELLED, user_id)
