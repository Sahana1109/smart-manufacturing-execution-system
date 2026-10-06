import uuid
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.modules.work_orders.models import WorkOrderStatus, WorkOrderPriority
from app.modules.products.schemas import ProductResponse
from app.modules.authentication.schemas import UserResponse
from app.modules.machines.schemas import MachineResponse
from app.modules.employees.schemas import EmployeeResponse


class WorkOrderCreate(BaseModel):
    work_order_number: Optional[str] = Field(None, description="Optional custom work order number. Auto-generated if omitted.")
    production_plan_id: uuid.UUID = Field(..., description="Target Production Plan ID")
    product_id: uuid.UUID = Field(..., description="Target Product SKU ID")
    planned_quantity: int = Field(..., gt=0, description="Quantity to produce (> 0)")
    start_date: date = Field(..., description="Target start date")
    due_date: date = Field(..., description="Target due completion date")
    priority: WorkOrderPriority = Field(default=WorkOrderPriority.MEDIUM)
    notes: Optional[str] = None
    assigned_machine_id: Optional[uuid.UUID] = None
    assigned_employee_id: Optional[uuid.UUID] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date, info) -> date:
        start_date = info.data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("due_date cannot be earlier than start_date")
        return v


class WorkOrderUpdate(BaseModel):
    planned_quantity: Optional[int] = Field(None, gt=0)
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    priority: Optional[WorkOrderPriority] = None
    notes: Optional[str] = None


class WorkOrderStatusUpdate(BaseModel):
    status: WorkOrderStatus = Field(..., description="Target status for state machine transition")


class WorkOrderAssignRequest(BaseModel):
    assigned_machine_id: Optional[uuid.UUID] = None
    assigned_employee_id: Optional[uuid.UUID] = None


class WorkOrderResponse(BaseModel):
    id: uuid.UUID
    work_order_number: str
    production_plan_id: uuid.UUID
    product_id: uuid.UUID
    product: Optional[ProductResponse] = None
    planned_quantity: int
    start_date: date
    due_date: date
    priority: WorkOrderPriority
    status: WorkOrderStatus
    notes: Optional[str] = None
    created_by_id: Optional[uuid.UUID] = None
    created_by: Optional[UserResponse] = None
    assigned_machine_id: Optional[uuid.UUID] = None
    assigned_machine: Optional[MachineResponse] = None
    assigned_employee_id: Optional[uuid.UUID] = None
    assigned_employee: Optional[EmployeeResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedWorkOrderResponse(BaseModel):
    items: List[WorkOrderResponse]
    total: int
    page: int
    limit: int
    pages: int
