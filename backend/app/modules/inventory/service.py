import uuid
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.inventory.models import Material, InventoryStock, StockMovement, MovementType
from app.modules.inventory.schemas import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    InventoryStockResponse,
    StockReceiptRequest,
    StockReservationRequest,
    StockReleaseRequest,
    StockConsumptionRequest,
    StockAdjustmentRequest,
    StockMovementResponse,
    InventoryDashboardSummary,
)
from app.modules.work_orders.models import WorkOrder
from app.modules.users.models import User
from app.modules.audit_logs.service import log_audit_event

logger = logging.getLogger(__name__)


def _build_material_response(mat: Material) -> MaterialResponse:
    stock_resp = None
    if mat.stock:
        stock_resp = InventoryStockResponse(
            id=mat.stock.id,
            material_id=mat.stock.material_id,
            quantity=mat.stock.quantity,
            reserved_quantity=mat.stock.reserved_quantity,
            available_quantity=mat.stock.available_quantity,
            location=mat.stock.location,
            updated_at=mat.stock.updated_at,
        )

    return MaterialResponse(
        id=mat.id,
        material_code=mat.material_code,
        name=mat.name,
        description=mat.description,
        unit=mat.unit,
        reorder_level=mat.reorder_level,
        is_active=mat.is_active,
        created_at=mat.created_at,
        updated_at=mat.updated_at,
        stock=stock_resp,
    )


def _build_movement_response(mv: StockMovement) -> StockMovementResponse:
    return StockMovementResponse(
        id=mv.id,
        material_id=mv.material_id,
        material_code=mv.material.material_code if mv.material else None,
        material_name=mv.material.name if mv.material else None,
        work_order_id=mv.work_order_id,
        work_order_number=mv.work_order.work_order_number if mv.work_order else None,
        movement_type=mv.movement_type,
        quantity=mv.quantity,
        reference=mv.reference,
        performed_by_id=mv.performed_by_id,
        performed_by_name=(
            f"{mv.performed_by.first_name} {mv.performed_by.last_name}".strip()
            if mv.performed_by and (mv.performed_by.first_name or mv.performed_by.last_name)
            else (mv.performed_by.username if mv.performed_by else None)
        ),
        created_at=mv.created_at,
    )


async def create_material(
    db: AsyncSession,
    payload: MaterialCreate,
    current_user: User,
) -> MaterialResponse:
    """
    Creates a new material and initializes its stock entry.
    """
    # 1. Unique material_code check
    stmt_code = select(Material).where(Material.material_code == payload.material_code.strip())
    res_code = await db.execute(stmt_code)
    if res_code.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Material code '{payload.material_code}' already exists"
        )

    # 2. Create Material Entity
    material = Material(
        material_code=payload.material_code.strip().upper(),
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        unit=payload.unit,
        reorder_level=payload.reorder_level,
        is_active=payload.is_active,
    )
    db.add(material)
    await db.flush()

    # 3. Create Stock Entry
    stock = InventoryStock(
        material_id=material.id,
        quantity=payload.initial_quantity or 0,
        reserved_quantity=0,
        location=payload.location or "MAIN-WAREHOUSE",
    )
    db.add(stock)
    await db.flush()

    # 4. If initial quantity > 0, log RECEIPT movement
    if payload.initial_quantity and payload.initial_quantity > 0:
        movement = StockMovement(
            material_id=material.id,
            movement_type=MovementType.RECEIPT,
            quantity=payload.initial_quantity,
            reference="Initial Stock Registration",
            performed_by_id=current_user.id,
        )
        db.add(movement)

    # 5. Audit Log
    await log_audit_event(
        db,
        action="MATERIAL_CREATED",
        entity_type="Material",
        entity_id=str(material.id),
        user_id=current_user.id,
        details={"code": material.material_code, "name": material.name, "initial_qty": payload.initial_quantity}
    )

    await db.commit()

    # Re-fetch with stock relationship
    stmt_full = select(Material).options(selectinload(Material.stock)).where(Material.id == material.id)
    res_full = await db.execute(stmt_full)
    full_mat = res_full.scalar_one()

    return _build_material_response(full_mat)


async def get_material_by_id(db: AsyncSession, material_id: uuid.UUID) -> MaterialResponse:
    """
    Fetches material details by ID.
    """
    stmt = select(Material).options(selectinload(Material.stock)).where(Material.id == material_id)
    res = await db.execute(stmt)
    material = res.scalar_one_or_none()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with ID '{material_id}' not found"
        )
    return _build_material_response(material)


async def list_materials(
    db: AsyncSession,
    search: Optional[str] = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> List[MaterialResponse]:
    """
    Lists materials matching filters.
    """
    stmt = select(Material).options(selectinload(Material.stock)).order_by(desc(Material.created_at))

    if active_only:
        stmt = stmt.where(Material.is_active == True)

    if search:
        term = f"%{search.strip()}%"
        stmt = stmt.where(or_(Material.material_code.ilike(term), Material.name.ilike(term)))

    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    materials = res.scalars().all()

    return [_build_material_response(m) for m in materials]


async def update_material(
    db: AsyncSession,
    material_id: uuid.UUID,
    payload: MaterialUpdate,
    current_user: User,
) -> MaterialResponse:
    """
    Updates material properties.
    """
    stmt = select(Material).options(selectinload(Material.stock)).where(Material.id == material_id)
    res = await db.execute(stmt)
    material = res.scalar_one_or_none()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with ID '{material_id}' not found"
        )

    if payload.name is not None:
        material.name = payload.name.strip()
    if payload.description is not None:
        material.description = payload.description.strip() if payload.description else None
    if payload.unit is not None:
        material.unit = payload.unit
    if payload.reorder_level is not None:
        material.reorder_level = payload.reorder_level
    if payload.is_active is not None:
        material.is_active = payload.is_active

    await log_audit_event(
        db,
        action="MATERIAL_UPDATED",
        entity_type="Material",
        entity_id=str(material.id),
        user_id=current_user.id,
        details={"name": material.name, "is_active": material.is_active}
    )

    await db.commit()
    await db.refresh(material)

    return _build_material_response(material)


async def delete_material(db: AsyncSession, material_id: uuid.UUID, current_user: User) -> dict:
    """
    Deactivates or soft-deletes a material.
    """
    stmt = select(Material).options(selectinload(Material.stock)).where(Material.id == material_id)
    res = await db.execute(stmt)
    material = res.scalar_one_or_none()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with ID '{material_id}' not found"
        )

    # Deactivate material to preserve stock movement history
    material.is_active = False

    await log_audit_event(
        db,
        action="MATERIAL_DEACTIVATED",
        entity_type="Material",
        entity_id=str(material.id),
        user_id=current_user.id,
    )

    await db.commit()

    return {"message": f"Material '{material.material_code}' deactivated successfully"}


# --- Stock Level Queries ---
async def get_stock_by_material_id(db: AsyncSession, material_id: uuid.UUID) -> InventoryStockResponse:
    """
    Fetches stock for a material.
    """
    stmt = select(InventoryStock).where(InventoryStock.material_id == material_id)
    res = await db.execute(stmt)
    stock = res.scalar_one_or_none()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock record for material ID '{material_id}' not found"
        )
    return InventoryStockResponse.model_validate(stock)


async def list_all_stocks(db: AsyncSession) -> List[InventoryStockResponse]:
    """
    Lists all stock records.
    """
    stmt = select(InventoryStock)
    res = await db.execute(stmt)
    stocks = res.scalars().all()
    return [InventoryStockResponse.model_validate(s) for s in stocks]


# --- Stock Operations ---
async def record_stock_receipt(
    db: AsyncSession,
    payload: StockReceiptRequest,
    current_user: User,
) -> InventoryStockResponse:
    """
    Receives material into inventory, increasing total stock.
    """
    stmt = select(Material).options(selectinload(Material.stock)).where(Material.id == payload.material_id)
    res = await db.execute(stmt)
    material = res.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    if not material.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot receive stock for an inactive material")

    stock = material.stock
    if not stock:
        stock = InventoryStock(material_id=material.id, quantity=0, reserved_quantity=0, location=payload.location or "MAIN-WAREHOUSE")
        db.add(stock)
        await db.flush()

    stock.quantity += payload.quantity
    if payload.location:
        stock.location = payload.location

    # Record Movement
    mv = StockMovement(
        material_id=material.id,
        movement_type=MovementType.RECEIPT,
        quantity=payload.quantity,
        reference=payload.reference or "Stock Receipt",
        performed_by_id=current_user.id,
    )
    db.add(mv)

    await log_audit_event(
        db,
        action="STOCK_RECEIVED",
        entity_type="InventoryStock",
        entity_id=str(stock.id),
        user_id=current_user.id,
        details={"qty_received": payload.quantity, "new_total": stock.quantity}
    )

    await db.commit()
    await db.refresh(stock)

    return InventoryStockResponse.model_validate(stock)


async def record_stock_reservation(
    db: AsyncSession,
    payload: StockReservationRequest,
    current_user: User,
) -> InventoryStockResponse:
    """
    Reserves available stock for a Work Order or allocation.
    """
    stmt = select(Material).options(selectinload(Material.stock)).where(Material.id == payload.material_id)
    res = await db.execute(stmt)
    material = res.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    if not material.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot reserve stock for an inactive material")

    stock = material.stock
    if not stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock entry not found for material")

    # Validate work order if provided
    if payload.work_order_id:
        wo_res = await db.execute(select(WorkOrder).where(WorkOrder.id == payload.work_order_id))
        if not wo_res.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Work Order '{payload.work_order_id}' not found")

    # Validate Available Quantity
    avail = stock.available_quantity
    if payload.quantity > avail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient available stock ({avail} available, {payload.quantity} requested for reservation)"
        )

    stock.reserved_quantity += payload.quantity

    # Record Movement
    mv = StockMovement(
        material_id=material.id,
        work_order_id=payload.work_order_id,
        movement_type=MovementType.RESERVATION,
        quantity=payload.quantity,
        reference=payload.reference or "Stock Reservation",
        performed_by_id=current_user.id,
    )
    db.add(mv)

    await log_audit_event(
        db,
        action="STOCK_RESERVED",
        entity_type="InventoryStock",
        entity_id=str(stock.id),
        user_id=current_user.id,
        details={"qty_reserved": payload.quantity, "total_reserved": stock.reserved_quantity}
    )

    await db.commit()
    await db.refresh(stock)

    return InventoryStockResponse.model_validate(stock)


async def record_stock_release(
    db: AsyncSession,
    payload: StockReleaseRequest,
    current_user: User,
) -> InventoryStockResponse:
    """
    Releases previously reserved stock back to available stock.
    """
    stmt = select(Material).options(selectinload(Material.stock)).where(Material.id == payload.material_id)
    res = await db.execute(stmt)
    material = res.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    stock = material.stock
    if not stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock entry not found")

    if payload.quantity > stock.reserved_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Release quantity ({payload.quantity}) exceeds currently reserved quantity ({stock.reserved_quantity})"
        )

    stock.reserved_quantity -= payload.quantity

    # Record Movement
    mv = StockMovement(
        material_id=material.id,
        work_order_id=payload.work_order_id,
        movement_type=MovementType.RELEASE,
        quantity=payload.quantity,
        reference=payload.reference or "Stock Release",
        performed_by_id=current_user.id,
    )
    db.add(mv)

    await log_audit_event(
        db,
        action="STOCK_RELEASED",
        entity_type="InventoryStock",
        entity_id=str(stock.id),
        user_id=current_user.id,
        details={"qty_released": payload.quantity, "remaining_reserved": stock.reserved_quantity}
    )

    await db.commit()
    await db.refresh(stock)

    return InventoryStockResponse.model_validate(stock)


async def record_stock_consumption(
    db: AsyncSession,
    payload: StockConsumptionRequest,
    current_user: User,
) -> InventoryStockResponse:
    """
    Consumes material stock during work order execution.
    """
    stmt = select(Material).options(selectinload(Material.stock)).where(Material.id == payload.material_id)
    res = await db.execute(stmt)
    material = res.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    if not material.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot consume an inactive material")

    stock = material.stock
    if not stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock entry not found")

    # Validate work order if provided
    if payload.work_order_id:
        wo_res = await db.execute(select(WorkOrder).where(WorkOrder.id == payload.work_order_id))
        if not wo_res.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Work Order '{payload.work_order_id}' not found")

    if payload.quantity > stock.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Consumption quantity ({payload.quantity}) exceeds total stock quantity ({stock.quantity})"
        )

    # Deduct total quantity and update reserved quantity if reserved
    stock.quantity -= payload.quantity
    stock.reserved_quantity = max(0, stock.reserved_quantity - payload.quantity)

    # Record Movement
    mv = StockMovement(
        material_id=material.id,
        work_order_id=payload.work_order_id,
        movement_type=MovementType.CONSUMPTION,
        quantity=payload.quantity,
        reference=payload.reference or "Stock Consumption",
        performed_by_id=current_user.id,
    )
    db.add(mv)

    await log_audit_event(
        db,
        action="STOCK_CONSUMED",
        entity_type="InventoryStock",
        entity_id=str(stock.id),
        user_id=current_user.id,
        details={"qty_consumed": payload.quantity, "remaining_stock": stock.quantity}
    )

    await db.commit()
    await db.refresh(stock)

    return InventoryStockResponse.model_validate(stock)


async def record_stock_adjustment(
    db: AsyncSession,
    payload: StockAdjustmentRequest,
    current_user: User,
) -> InventoryStockResponse:
    """
    Adjusts stock quantity to target level, logging an ADJUSTMENT movement.
    """
    stmt = select(Material).options(selectinload(Material.stock)).where(Material.id == payload.material_id)
    res = await db.execute(stmt)
    material = res.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    stock = material.stock
    if not stock:
        stock = InventoryStock(material_id=material.id, quantity=0, reserved_quantity=0, location="MAIN-WAREHOUSE")
        db.add(stock)
        await db.flush()

    delta = payload.new_quantity - stock.quantity
    stock.quantity = payload.new_quantity
    stock.reserved_quantity = min(stock.reserved_quantity, stock.quantity)

    # Record Movement
    mv = StockMovement(
        material_id=material.id,
        movement_type=MovementType.ADJUSTMENT,
        quantity=delta,
        reference=payload.reference,
        performed_by_id=current_user.id,
    )
    db.add(mv)

    await log_audit_event(
        db,
        action="STOCK_ADJUSTED",
        entity_type="InventoryStock",
        entity_id=str(stock.id),
        user_id=current_user.id,
        details={"delta": delta, "new_quantity": payload.new_quantity, "reason": payload.reference}
    )

    await db.commit()
    await db.refresh(stock)

    return InventoryStockResponse.model_validate(stock)


# --- Movements & Low Stock Queries ---
async def list_stock_movements(
    db: AsyncSession,
    material_id: Optional[uuid.UUID] = None,
    movement_type: Optional[MovementType] = None,
    work_order_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[StockMovementResponse]:
    """
    Lists stock movements matching filters sorted by creation date descending.
    """
    stmt = (
        select(StockMovement)
        .options(
            selectinload(StockMovement.material),
            selectinload(StockMovement.work_order),
            selectinload(StockMovement.performed_by),
        )
        .order_by(desc(StockMovement.created_at))
    )

    if material_id:
        stmt = stmt.where(StockMovement.material_id == material_id)
    if movement_type:
        stmt = stmt.where(StockMovement.movement_type == movement_type)
    if work_order_id:
        stmt = stmt.where(StockMovement.work_order_id == work_order_id)

    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    movements = res.scalars().all()

    return [_build_movement_response(mv) for mv in movements]


async def get_low_stock_materials(db: AsyncSession) -> List[MaterialResponse]:
    """
    Retrieves active materials where available_quantity <= reorder_level.
    """
    stmt = (
        select(Material)
        .join(Material.stock)
        .options(selectinload(Material.stock))
        .where(Material.is_active == True)
        .where((InventoryStock.quantity - InventoryStock.reserved_quantity) <= Material.reorder_level)
        .order_by(Material.material_code)
    )
    res = await db.execute(stmt)
    materials = res.scalars().all()

    return [_build_material_response(m) for m in materials]


async def get_inventory_dashboard_summary(db: AsyncSession) -> InventoryDashboardSummary:
    """
    Aggregates inventory dashboard stats.
    """
    # Total materials
    res_mat = await db.execute(select(func.count(Material.id)))
    total_materials = res_mat.scalar() or 0

    # Total stock items (materials with stock)
    res_stock = await db.execute(select(func.count(InventoryStock.id)))
    total_stock_items = res_stock.scalar() or 0

    # Low stock count
    stmt_low = (
        select(func.count(Material.id))
        .join(Material.stock)
        .where(Material.is_active == True)
        .where((InventoryStock.quantity - InventoryStock.reserved_quantity) <= Material.reorder_level)
    )
    res_low = await db.execute(stmt_low)
    low_stock_count = res_low.scalar() or 0

    # Total reserved quantity across all stock
    res_reserved = await db.execute(select(func.coalesce(func.sum(InventoryStock.reserved_quantity), 0)))
    total_reserved = res_reserved.scalar() or 0

    return InventoryDashboardSummary(
        total_materials=total_materials,
        total_stock_items=total_stock_items,
        low_stock_count=low_stock_count,
        total_reserved_quantity=total_reserved,
    )
