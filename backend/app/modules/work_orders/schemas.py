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
    produced_quantity: Optional[int] = Field(None, ge=0)
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    priority: Optional[WorkOrderPriority] = None
    notes: Optional[str] = None


class WorkOrderStatusUpdate(BaseModel):
    status: WorkOrderStatus = Field(..., description="Target status for state machine transition")


class WorkOrderAssignRequest(BaseModel):
    assigned_machine_id: Optional[uuid.UUID] = None
    assigned_employee_id: Optional[uuid.UUID] = None


class WorkOrderPauseRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Reason for pausing execution")


class WorkOrderCompleteRequest(BaseModel):
    produced_quantity: int = Field(..., gt=0, description="Final produced quantity (> 0)")
    notes: Optional[str] = Field(None, description="Completion remarks")


class DowntimeRecordCreate(BaseModel):
    work_order_id: uuid.UUID = Field(..., description="Associated Work Order ID")
    machine_id: Optional[uuid.UUID] = Field(None, description="Associated Machine ID")
    start_time: datetime = Field(..., description="Downtime start timestamp")
    end_time: Optional[datetime] = Field(None, description="Downtime resolution timestamp")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Downtime duration in minutes")
    reason: str = Field(..., description="Reason category (e.g. MACHINE_BREAKDOWN, MATERIAL_UNAVAILABLE, MAINTENANCE, POWER_FAILURE, OTHER)")
    remarks: Optional[str] = Field(None, description="Detailed downtime remarks")


class DowntimeRecordResponse(BaseModel):
    id: uuid.UUID
    work_order_id: uuid.UUID
    machine_id: Optional[uuid.UUID] = None
    machine: Optional[MachineResponse] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    reason: str
    remarks: Optional[str] = None
    recorded_by_id: Optional[uuid.UUID] = None
    recorded_by: Optional[UserResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkOrderResponse(BaseModel):
    id: uuid.UUID
    work_order_number: str
    production_plan_id: uuid.UUID
    product_id: uuid.UUID
    product: Optional[ProductResponse] = None
    planned_quantity: int
    produced_quantity: int = 0
    remaining_quantity: int = 0
    progress_percentage: float = 0.0
    start_date: date
    due_date: date
    actual_start_time: Optional[datetime] = None
    actual_completion_time: Optional[datetime] = None
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


class WorkOrderExecutionResponse(BaseModel):
    work_order: WorkOrderResponse
    downtime_records: List[DowntimeRecordResponse] = []
    total_downtime_minutes: int = 0


class PaginatedWorkOrderResponse(BaseModel):
    items: List[WorkOrderResponse]
    total: int
    page: int
    limit: int
    pages: int
