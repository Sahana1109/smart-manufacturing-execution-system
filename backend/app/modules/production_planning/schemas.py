import uuid
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.modules.production_planning.models import ProductionPlanStatus, ProductionPlanPriority
from app.modules.products.schemas import ProductResponse
from app.modules.authentication.schemas import UserResponse


class ProductionPlanCreate(BaseModel):
    plan_number: Optional[str] = Field(None, description="Optional custom plan number. Auto-generated if omitted.")
    product_id: uuid.UUID = Field(..., description="Target product SKU ID")
    planned_quantity: int = Field(..., gt=0, description="Target quantity to manufacture (> 0)")
    start_date: date = Field(..., description="Planned execution start date")
    due_date: date = Field(..., description="Planned execution completion due date")
    priority: ProductionPlanPriority = Field(default=ProductionPlanPriority.MEDIUM)
    notes: Optional[str] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date, info) -> date:
        start_date = info.data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("due_date cannot be earlier than start_date")
        return v


class ProductionPlanUpdate(BaseModel):
    planned_quantity: Optional[int] = Field(None, gt=0)
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    priority: Optional[ProductionPlanPriority] = None
    notes: Optional[str] = None


class ProductionPlanStatusUpdate(BaseModel):
    status: ProductionPlanStatus = Field(..., description="Target status for state machine transition")


class ProductionPlanResponse(BaseModel):
    id: uuid.UUID
    plan_number: str
    product_id: uuid.UUID
    product: Optional[ProductResponse] = None
    planned_quantity: int
    start_date: date
    due_date: date
    priority: ProductionPlanPriority
    status: ProductionPlanStatus
    notes: Optional[str] = None
    created_by_id: Optional[uuid.UUID] = None
    created_by: Optional[UserResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedProductionPlanResponse(BaseModel):
    items: List[ProductionPlanResponse]
    total: int
    page: int
    limit: int
    pages: int
