import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.modules.inventory.schemas import MaterialResponse, StockMovementResponse


class ProductionReportResponse(BaseModel):
    total_work_orders: int = 0
    pending: int = 0
    in_progress: int = 0
    paused: int = 0
    completed: int = 0
    closed: int = 0
    cancelled: int = 0
    completion_percentage: float = 0.0
    total_planned_quantity: int = 0
    total_produced_quantity: int = 0


class QualityReportResponse(BaseModel):
    total_inspections: int = 0
    pending: int = 0
    passed: int = 0
    failed: int = 0
    rework_required: int = 0
    total_inspected_quantity: int = 0
    total_accepted_quantity: int = 0
    total_rejected_quantity: int = 0
    total_defects: int = 0


class InventoryReportResponse(BaseModel):
    total_materials: int = 0
    total_stock_items: int = 0
    total_quantity: int = 0
    total_reserved_quantity: int = 0
    total_available_quantity: int = 0
    low_stock_count: int = 0
    low_stock_materials: List[MaterialResponse] = []
    recent_movements: List[StockMovementResponse] = []


class MachineReportResponse(BaseModel):
    total_machines: int = 0
    operational: int = 0
    in_use: int = 0
    maintenance: int = 0
    inactive: int = 0


class OperatorReportResponse(BaseModel):
    total_operators: int = 0
    active_operators: int = 0
    assigned_operators: int = 0
    unassigned_operators: int = 0


class DashboardSummaryResponse(BaseModel):
    production: ProductionReportResponse
    quality: QualityReportResponse
    inventory: InventoryReportResponse
    machines: MachineReportResponse
    operators: OperatorReportResponse
