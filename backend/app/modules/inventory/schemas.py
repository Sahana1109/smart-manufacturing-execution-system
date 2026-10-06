import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.modules.inventory.models import MaterialUnit, MovementType


# --- Stock Level Schema ---
class InventoryStockResponse(BaseModel):
    id: uuid.UUID
    material_id: uuid.UUID
    quantity: int = 0
    reserved_quantity: int = 0
    available_quantity: int = 0
    location: str = "MAIN-WAREHOUSE"
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Material Schemas ---
class MaterialBase(BaseModel):
    material_code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    unit: MaterialUnit = MaterialUnit.PCS
    reorder_level: int = Field(default=10, ge=0)
    is_active: bool = True


class MaterialCreate(MaterialBase):
    initial_quantity: Optional[int] = Field(default=0, ge=0)
    location: Optional[str] = "MAIN-WAREHOUSE"


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[MaterialUnit] = None
    reorder_level: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class MaterialResponse(MaterialBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    stock: Optional[InventoryStockResponse] = None

    model_config = ConfigDict(from_attributes=True)


# --- Stock Operation Requests ---
class StockReceiptRequest(BaseModel):
    material_id: uuid.UUID
    quantity: int = Field(..., gt=0, description="Quantity received (> 0)")
    location: Optional[str] = "MAIN-WAREHOUSE"
    reference: Optional[str] = None


class StockReservationRequest(BaseModel):
    material_id: uuid.UUID
    work_order_id: Optional[uuid.UUID] = None
    quantity: int = Field(..., gt=0, description="Quantity to reserve (> 0)")
    reference: Optional[str] = None


class StockReleaseRequest(BaseModel):
    material_id: uuid.UUID
    work_order_id: Optional[uuid.UUID] = None
    quantity: int = Field(..., gt=0, description="Quantity to release (> 0)")
    reference: Optional[str] = None


class StockConsumptionRequest(BaseModel):
    material_id: uuid.UUID
    work_order_id: Optional[uuid.UUID] = None
    quantity: int = Field(..., gt=0, description="Quantity to consume (> 0)")
    reference: Optional[str] = None


class StockAdjustmentRequest(BaseModel):
    material_id: uuid.UUID
    new_quantity: int = Field(..., ge=0, description="Target updated total stock quantity (>= 0)")
    reference: str = Field(..., min_length=2, description="Adjustment reason/reference remark")


# --- Stock Movement Response ---
class StockMovementResponse(BaseModel):
    id: uuid.UUID
    material_id: uuid.UUID
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    work_order_id: Optional[uuid.UUID] = None
    work_order_number: Optional[str] = None
    movement_type: MovementType
    quantity: int
    reference: Optional[str] = None
    performed_by_id: Optional[uuid.UUID] = None
    performed_by_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Inventory Dashboard Summary ---
class InventoryDashboardSummary(BaseModel):
    total_materials: int = 0
    total_stock_items: int = 0
    low_stock_count: int = 0
    total_reserved_quantity: int = 0
