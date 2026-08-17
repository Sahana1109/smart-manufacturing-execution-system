import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user, require_roles
from app.modules.users.models import User
from app.modules.production_planning.models import ProductionPlanStatus, ProductionPlanPriority
from app.modules.production_planning import service as plan_service
from app.modules.production_planning.schemas import (
    ProductionPlanCreate,
    ProductionPlanUpdate,
    ProductionPlanStatusUpdate,
    ProductionPlanResponse,
    PaginatedProductionPlanResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=ProductionPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Production Plan (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def create_production_plan(
    plan_in: ProductionPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a new production plan in DRAFT status. Validates quantity, dates, and active product.
    Requires ADMIN or PRODUCTION_MANAGER role.
    """
    return await plan_service.create_production_plan(db, plan_in, user_id=current_user.id)


@router.get(
    "",
    response_model=PaginatedProductionPlanResponse,
    summary="List production plans with status/priority filtering and pagination"
)
async def list_production_plans(
    status_filter: Optional[ProductionPlanStatus] = Query(None, alias="status", description="Filter by status"),
    priority_filter: Optional[ProductionPlanPriority] = Query(None, alias="priority", description="Filter by priority"),
    product_id_filter: Optional[uuid.UUID] = Query(None, alias="product_id", description="Filter by product ID"),
    search: Optional[str] = Query(None, description="Search by plan number, product code, or name"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lists production plans matching filter parameters. Accessible to all authenticated roles.
    """
    items, total, pages = await plan_service.list_production_plans(
        db,
        status_filter=status_filter,
        priority_filter=priority_filter,
        product_id_filter=product_id_filter,
        search=search,
        page=page,
        limit=limit
    )
    return PaginatedProductionPlanResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get(
    "/{plan_id}",
    response_model=ProductionPlanResponse,
    summary="Get production plan details by ID"
)
async def get_production_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetches production plan details by ID. Accessible to all authenticated roles.
    """
    return await plan_service.get_production_plan_by_id(db, plan_id)


@router.put(
    "/{plan_id}",
    response_model=ProductionPlanResponse,
    summary="Update production plan details (Admin / Production Manager / Supervisor)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"))]
)
async def update_production_plan(
    plan_id: uuid.UUID,
    plan_update: ProductionPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates production plan quantity, dates, priority, or notes.
    Requires ADMIN, PRODUCTION_MANAGER, or SUPERVISOR role.
    """
    return await plan_service.update_production_plan(db, plan_id, plan_update, user_id=current_user.id)


@router.patch(
    "/{plan_id}/status",
    response_model=ProductionPlanResponse,
    summary="Transition production plan status (Admin / Production Manager / Supervisor)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR"))]
)
async def update_plan_status(
    plan_id: uuid.UUID,
    status_update: ProductionPlanStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Transitions production plan status according to state machine rules.
    Requires ADMIN, PRODUCTION_MANAGER, or SUPERVISOR role.
    """
    return await plan_service.change_plan_status(db, plan_id, status_update.status, user_id=current_user.id)


@router.post(
    "/{plan_id}/cancel",
    response_model=ProductionPlanResponse,
    summary="Cancel a production plan (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def cancel_production_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancels an existing active production plan. Requires ADMIN or PRODUCTION_MANAGER role.
    """
    return await plan_service.cancel_production_plan(db, plan_id, user_id=current_user.id)
