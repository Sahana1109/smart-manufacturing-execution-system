import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, require_roles
from app.modules.users.models import User
from app.modules.inventory.models import MovementType
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
from app.modules.inventory import service as inventory_service

router = APIRouter()

# Role Constants
READ_ROLES = ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR", "INVENTORY_MANAGER", "QUALITY_INSPECTOR", "OPERATOR"]
WRITE_ROLES = ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR", "INVENTORY_MANAGER"]
INVENTORY_ADMIN_ROLES = ["ADMIN", "INVENTORY_MANAGER"]


# --- Inventory Summary & Low Stock ---
@router.get(
    "/summary",
    response_model=InventoryDashboardSummary,
    summary="Get inventory summary metrics for dashboard",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def get_inventory_summary(
    db: AsyncSession = Depends(get_db),
):
    """
    Returns dashboard metrics: total materials, stock count, low stock count, and total reserved quantity.
    """
    return await inventory_service.get_inventory_dashboard_summary(db)


@router.get(
    "/low-stock",
    response_model=List[MaterialResponse],
    summary="List materials where available stock is below or equal to reorder level",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def get_low_stock_materials(
    db: AsyncSession = Depends(get_db),
):
    """
    Lists materials requiring re-order based on available stock level.
    """
    return await inventory_service.get_low_stock_materials(db)


# --- Material CRUD Endpoints ---
@router.post(
    "/materials",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new material master entity",
    dependencies=[Depends(require_roles(*INVENTORY_ADMIN_ROLES))],
)
async def create_material(
    payload: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new material and initializes its stock entry.
    """
    return await inventory_service.create_material(db, payload, current_user)


@router.get(
    "/materials",
    response_model=List[MaterialResponse],
    summary="List materials with optional search and active status filters",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def list_materials(
    search: Optional[str] = Query(None, description="Search term for code or name"),
    active_only: bool = Query(False, description="Filter only active materials"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists material master entries with stock levels preloaded.
    """
    return await inventory_service.list_materials(
        db, search=search, active_only=active_only, skip=skip, limit=limit
    )


@router.get(
    "/materials/{id}",
    response_model=MaterialResponse,
    summary="Get material details by ID",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def get_material(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves detailed material info including stock status.
    """
    return await inventory_service.get_material_by_id(db, id)


@router.patch(
    "/materials/{id}",
    response_model=MaterialResponse,
    summary="Update material properties",
    dependencies=[Depends(require_roles(*INVENTORY_ADMIN_ROLES))],
)
async def update_material(
    id: uuid.UUID,
    payload: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates material properties (name, description, unit, reorder_level, is_active).
    """
    return await inventory_service.update_material(db, id, payload, current_user)


@router.delete(
    "/materials/{id}",
    summary="Deactivate or delete material",
    dependencies=[Depends(require_roles(*INVENTORY_ADMIN_ROLES))],
)
async def delete_material(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deactivates a material entity.
    """
    return await inventory_service.delete_material(db, id, current_user)


# --- Stock Level Endpoints ---
@router.get(
    "/stock",
    response_model=List[InventoryStockResponse],
    summary="List all inventory stock levels",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def list_all_stocks(
    db: AsyncSession = Depends(get_db),
):
    """
    Lists stock records for all materials.
    """
    return await inventory_service.list_all_stocks(db)


@router.get(
    "/stock/{material_id}",
    response_model=InventoryStockResponse,
    summary="Get stock level for a specific material",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def get_stock_by_material(
    material_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves quantity, reserved, and available stock for a material.
    """
    return await inventory_service.get_stock_by_material_id(db, material_id)


# --- Stock Operation Endpoints ---
@router.post(
    "/stock/receipt",
    response_model=InventoryStockResponse,
    summary="Receive material stock into inventory",
    dependencies=[Depends(require_roles(*INVENTORY_ADMIN_ROLES))],
)
async def stock_receipt(
    payload: StockReceiptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Increases total stock quantity and logs a RECEIPT movement.
    """
    return await inventory_service.record_stock_receipt(db, payload, current_user)


@router.post(
    "/stock/reserve",
    response_model=InventoryStockResponse,
    summary="Reserve available stock for a Work Order",
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
async def stock_reserve(
    payload: StockReservationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reserves available stock and logs a RESERVATION movement.
    """
    return await inventory_service.record_stock_reservation(db, payload, current_user)


@router.post(
    "/stock/release",
    response_model=InventoryStockResponse,
    summary="Release reserved stock back to available pool",
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
async def stock_release(
    payload: StockReleaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Releases reserved stock and logs a RELEASE movement.
    """
    return await inventory_service.record_stock_release(db, payload, current_user)


@router.post(
    "/stock/consume",
    response_model=InventoryStockResponse,
    summary="Consume stock during work order execution",
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
async def stock_consume(
    payload: StockConsumptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deducts stock quantity and logs a CONSUMPTION movement.
    """
    return await inventory_service.record_stock_consumption(db, payload, current_user)


@router.post(
    "/stock/adjust",
    response_model=InventoryStockResponse,
    summary="Adjust stock to a new quantity level",
    dependencies=[Depends(require_roles(*INVENTORY_ADMIN_ROLES))],
)
async def stock_adjust(
    payload: StockAdjustmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Adjusts stock level to target value and logs an ADJUSTMENT movement.
    """
    return await inventory_service.record_stock_adjustment(db, payload, current_user)


# --- Stock Movements History ---
@router.get(
    "/movements",
    response_model=List[StockMovementResponse],
    summary="List stock movement history with optional filtering",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def list_movements(
    material_id: Optional[uuid.UUID] = Query(None, description="Filter by material ID"),
    movement_type: Optional[MovementType] = Query(None, description="Filter by movement type"),
    work_order_id: Optional[uuid.UUID] = Query(None, description="Filter by work order ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists audit log of stock movements sorted by date descending.
    """
    return await inventory_service.list_stock_movements(
        db,
        material_id=material_id,
        movement_type=movement_type,
        work_order_id=work_order_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/movements/{material_id}",
    response_model=List[StockMovementResponse],
    summary="List stock movement history for a specific material",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def list_movements_by_material(
    material_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists movement history for a specific material.
    """
    return await inventory_service.list_stock_movements(
        db, material_id=material_id, skip=skip, limit=limit
    )
