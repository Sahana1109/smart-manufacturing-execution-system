import uuid
import math
from typing import List, Optional, Tuple
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.production_planning.models import ProductionPlan, ProductionPlanStatus, ProductionPlanPriority
from app.modules.products.models import Product
from app.modules.production_planning.schemas import ProductionPlanCreate, ProductionPlanUpdate
from app.modules.audit_logs.service import log_audit_event

ALLOWED_STATUS_TRANSITIONS = {
    ProductionPlanStatus.DRAFT: [ProductionPlanStatus.PLANNED, ProductionPlanStatus.CANCELLED],
    ProductionPlanStatus.PLANNED: [ProductionPlanStatus.IN_PROGRESS, ProductionPlanStatus.CANCELLED],
    ProductionPlanStatus.IN_PROGRESS: [ProductionPlanStatus.COMPLETED, ProductionPlanStatus.CANCELLED],
    ProductionPlanStatus.COMPLETED: [],
    ProductionPlanStatus.CANCELLED: [],
}


async def generate_plan_number(db: AsyncSession) -> str:
    """
    Generates next sequential plan number in format PP-YYYY-XXXX.
    """
    current_year = datetime.now().year
    prefix = f"PP-{current_year}-"
    
    stmt = select(func.count(ProductionPlan.id)).where(ProductionPlan.plan_number.like(f"{prefix}%"))
    res = await db.execute(stmt)
    count = res.scalar() or 0
    
    return f"{prefix}{count + 1:04d}"


async def create_production_plan(
    db: AsyncSession,
    plan_in: ProductionPlanCreate,
    user_id: uuid.UUID
) -> ProductionPlan:
    """
    Creates a new production plan with domain validation and audit logging.
    """
    # 1. Quantity validation
    if plan_in.planned_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="planned_quantity must be greater than 0"
        )

    # 2. Date range validation
    if plan_in.start_date > plan_in.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be after due_date"
        )

    # 3. Product existence & active status validation
    prod_stmt = select(Product).where(Product.id == plan_in.product_id)
    prod_res = await db.execute(prod_stmt)
    product = prod_res.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{plan_in.product_id}' not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot schedule production plan for inactive product '{product.name}'"
        )

    # 4. Plan number resolution & uniqueness
    plan_number = plan_in.plan_number.strip() if plan_in.plan_number else await generate_plan_number(db)
    
    num_stmt = select(ProductionPlan).where(ProductionPlan.plan_number == plan_number)
    num_res = await db.execute(num_stmt)
    if num_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Production plan number '{plan_number}' already exists"
        )

    # 5. Create Entity
    new_plan = ProductionPlan(
        plan_number=plan_number,
        product_id=plan_in.product_id,
        planned_quantity=plan_in.planned_quantity,
        start_date=plan_in.start_date,
        due_date=plan_in.due_date,
        priority=plan_in.priority,
        status=ProductionPlanStatus.DRAFT,
        notes=plan_in.notes,
        created_by_id=user_id,
    )
    db.add(new_plan)
    await db.flush()

    # 6. Record Audit Event
    await log_audit_event(
        db,
        action="PRODUCTION_PLAN_CREATED",
        entity_type="ProductionPlan",
        entity_id=str(new_plan.id),
        user_id=user_id,
        details={
            "plan_number": new_plan.plan_number,
            "product_code": product.product_code,
            "planned_quantity": new_plan.planned_quantity,
            "status": new_plan.status.value,
        }
    )

    await db.commit()
    
    # Reload with relationships
    return await get_production_plan_by_id(db, new_plan.id)  # type: ignore


async def get_production_plan_by_id(db: AsyncSession, plan_id: uuid.UUID) -> ProductionPlan:
    """
    Fetches production plan by ID with product and user relationships loaded.
    """
    stmt = (
        select(ProductionPlan)
        .where(ProductionPlan.id == plan_id)
        .options(selectinload(ProductionPlan.product), selectinload(ProductionPlan.created_by))
    )
    res = await db.execute(stmt)
    plan = res.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production plan with ID '{plan_id}' not found"
        )
    return plan


async def list_production_plans(
    db: AsyncSession,
    status_filter: Optional[ProductionPlanStatus] = None,
    priority_filter: Optional[ProductionPlanPriority] = None,
    product_id_filter: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> Tuple[List[ProductionPlan], int, int]:
    """
    Lists production plans with filtering, search, and pagination.
    Returns (items, total_count, total_pages).
    """
    stmt = select(ProductionPlan).options(
        selectinload(ProductionPlan.product),
        selectinload(ProductionPlan.created_by)
    )
    
    conditions = []
    if status_filter:
        conditions.append(ProductionPlan.status == status_filter)
    if priority_filter:
        conditions.append(ProductionPlan.priority == priority_filter)
    if product_id_filter:
        conditions.append(ProductionPlan.product_id == product_id_filter)
    if search:
        search_term = f"%{search.strip()}%"
        # Join product to enable searching by product code or name
        stmt = stmt.join(ProductionPlan.product)
        conditions.append(
            or_(
                ProductionPlan.plan_number.ilike(search_term),
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
    stmt = stmt.order_by(ProductionPlan.created_at.desc()).offset(offset).limit(limit)
    res = await db.execute(stmt)
    items = list(res.scalars().all())

    return items, total, pages


async def update_production_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
    plan_update: ProductionPlanUpdate,
    user_id: uuid.UUID
) -> ProductionPlan:
    """
    Updates production plan parameters with business validation and audit logging.
    """
    plan = await get_production_plan_by_id(db, plan_id)

    if plan.status in (ProductionPlanStatus.COMPLETED, ProductionPlanStatus.CANCELLED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update a production plan that is already {plan.status.value}"
        )

    # Date validation
    start_d = plan_update.start_date or plan.start_date
    due_d = plan_update.due_date or plan.due_date
    if start_d > due_d:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be after due_date"
        )

    updated_fields = {}
    if plan_update.planned_quantity is not None:
        plan.planned_quantity = plan_update.planned_quantity
        updated_fields["planned_quantity"] = plan_update.planned_quantity
    if plan_update.start_date is not None:
        plan.start_date = plan_update.start_date
        updated_fields["start_date"] = str(plan_update.start_date)
    if plan_update.due_date is not None:
        plan.due_date = plan_update.due_date
        updated_fields["due_date"] = str(plan_update.due_date)
    if plan_update.priority is not None:
        plan.priority = plan_update.priority
        updated_fields["priority"] = plan_update.priority.value
    if plan_update.notes is not None:
        plan.notes = plan_update.notes
        updated_fields["notes"] = plan_update.notes

    if updated_fields:
        await log_audit_event(
            db,
            action="PRODUCTION_PLAN_UPDATED",
            entity_type="ProductionPlan",
            entity_id=str(plan.id),
            user_id=user_id,
            details=updated_fields
        )

    await db.commit()
    await db.refresh(plan)
    return plan


async def change_plan_status(
    db: AsyncSession,
    plan_id: uuid.UUID,
    target_status: ProductionPlanStatus,
    user_id: uuid.UUID
) -> ProductionPlan:
    """
    Executes controlled status state machine transitions.
    """
    plan = await get_production_plan_by_id(db, plan_id)
    current_status = plan.status

    if target_status == current_status:
        return plan

    allowed_next = ALLOWED_STATUS_TRANSITIONS.get(current_status, [])
    if target_status not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status.value}' to '{target_status.value}'. Allowed transitions: {[s.value for s in allowed_next]}"
        )

    plan.status = target_status

    await log_audit_event(
        db,
        action="PRODUCTION_PLAN_STATUS_CHANGED",
        entity_type="ProductionPlan",
        entity_id=str(plan.id),
        user_id=user_id,
        details={
            "from_status": current_status.value,
            "to_status": target_status.value,
        }
    )

    await db.commit()
    await db.refresh(plan)
    return plan


async def cancel_production_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
    user_id: uuid.UUID
) -> ProductionPlan:
    """
    Cancels an existing active production plan.
    """
    return await change_plan_status(db, plan_id, ProductionPlanStatus.CANCELLED, user_id)
