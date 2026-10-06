import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user, require_roles
from app.modules.users.models import User
from app.modules.work_orders.models import WorkOrderStatus, WorkOrderPriority
from app.modules.work_orders import service as wo_service
from app.modules.work_orders.schemas import (
    WorkOrderCreate,
    WorkOrderUpdate,
    WorkOrderStatusUpdate,
    WorkOrderAssignRequest,
    WorkOrderResponse,
    PaginatedWorkOrderResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=WorkOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Work Order (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def create_work_order(
    order_in: WorkOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a new work order linked to a Production Plan. Requires ADMIN or PRODUCTION_MANAGER role.
    """
    return await wo_service.create_work_order(db, order_in, user_id=current_user.id)


@router.get(
    "",
    response_model=PaginatedWorkOrderResponse,
    summary="List work orders with status/priority filtering and pagination"
)
async def list_work_orders(
    status_filter: Optional[WorkOrderStatus] = Query(None, alias="status", description="Filter by status"),
    priority_filter: Optional[WorkOrderPriority] = Query(None, alias="priority", description="Filter by priority"),
    plan_id_filter: Optional[uuid.UUID] = Query(None, alias="production_plan_id", description="Filter by production plan ID"),
    product_id_filter: Optional[uuid.UUID] = Query(None, alias="product_id", description="Filter by product ID"),
    search: Optional[str] = Query(None, description="Search by work order number, product code, or name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lists work orders. Accessible to all authenticated roles.
    """
    items, total, pages = await wo_service.list_work_orders(
        db,
        status_filter=status_filter,
        priority_filter=priority_filter,
        plan_id_filter=plan_id_filter,
        product_id_filter=product_id_filter,
        search=search,
        page=page,
        limit=limit
    )
    return PaginatedWorkOrderResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get(
    "/{order_id}",
    response_model=WorkOrderResponse,
    summary="Get work order details by ID"
)
async def get_work_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetches work order details by ID. Accessible to all authenticated roles.
    """
    return await wo_service.get_work_order_by_id(db, order_id)


@router.put(
    "/{order_id}",
    response_model=WorkOrderResponse,
    summary="Update work order details (Admin / Production Manager / Supervisor)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"))]
)
async def update_work_order(
    order_id: uuid.UUID,
    order_update: WorkOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates work order quantity, dates, priority, or notes.
    """
    return await wo_service.update_work_order(db, order_id, order_update, user_id=current_user.id)


@router.patch(
    "/{order_id}/status",
    response_model=WorkOrderResponse,
    summary="Transition work order status (Admin / Production Manager / Supervisor / Operator)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR", "OPERATOR"))]
)
async def update_work_order_status(
    order_id: uuid.UUID,
    status_update: WorkOrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Transitions work order status according to state machine rules.
    """
    user_roles = [r.name for r in current_user.roles] if current_user.roles else []
    return await wo_service.change_work_order_status(
        db, order_id, status_update.status, user_id=current_user.id, user_roles=user_roles
    )


@router.patch(
    "/{order_id}/assign",
    response_model=WorkOrderResponse,
    summary="Assign machine and/or operator (Admin / Production Manager / Supervisor)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"))]
)
async def assign_work_order(
    order_id: uuid.UUID,
    assign_in: WorkOrderAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Assigns machine and/or employee to a work order.
    """
    return await wo_service.assign_work_order(db, order_id, assign_in, user_id=current_user.id)


@router.delete(
    "/{order_id}/assign/machine",
    response_model=WorkOrderResponse,
    summary="Unassign machine from work order (Admin / Production Manager / Supervisor)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"))]
)
async def unassign_machine_from_work_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Unassigns machine from a work order.
    """
    return await wo_service.unassign_work_order_resource(
        db, order_id, unassign_machine=True, user_id=current_user.id
    )


@router.delete(
    "/{order_id}/assign/employee",
    response_model=WorkOrderResponse,
    summary="Unassign employee operator from work order (Admin / Production Manager / Supervisor)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"))]
)
async def unassign_employee_from_work_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Unassigns employee operator from a work order.
    """
    return await wo_service.unassign_work_order_resource(
        db, order_id, unassign_employee=True, user_id=current_user.id
    )


@router.post(
    "/{order_id}/cancel",
    response_model=WorkOrderResponse,
    summary="Cancel a work order (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def cancel_work_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancels an active work order. Requires ADMIN or PRODUCTION_MANAGER role.
    """
    return await wo_service.cancel_work_order(db, order_id, user_id=current_user.id)
