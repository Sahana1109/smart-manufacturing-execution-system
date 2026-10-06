import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.modules.quality.models import QualityStatus, DefectType, DefectSeverity


# Defect Schemas
class QualityDefectBase(BaseModel):
    defect_type: DefectType = DefectType.OTHER
    severity: DefectSeverity = DefectSeverity.MEDIUM
    description: Optional[str] = None
    quantity: int = Field(default=1, ge=0)
    remarks: Optional[str] = None


class QualityDefectCreate(QualityDefectBase):
    pass


class QualityDefectUpdate(BaseModel):
    defect_type: Optional[DefectType] = None
    severity: Optional[DefectSeverity] = None
    description: Optional[str] = None
    quantity: Optional[int] = Field(default=None, ge=0)
    remarks: Optional[str] = None


class QualityDefectResponse(QualityDefectBase):
    id: uuid.UUID
    inspection_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Inspection Schemas
class QualityInspectionCreate(BaseModel):
    work_order_id: uuid.UUID
    inspected_quantity: int = Field(default=0, ge=0)
    accepted_quantity: int = Field(default=0, ge=0)
    rejected_quantity: int = Field(default=0, ge=0)
    status: QualityStatus = QualityStatus.PENDING
    remarks: Optional[str] = None


class QualityInspectionUpdate(BaseModel):
    inspected_quantity: Optional[int] = Field(default=None, ge=0)
    accepted_quantity: Optional[int] = Field(default=None, ge=0)
    rejected_quantity: Optional[int] = Field(default=None, ge=0)
    status: Optional[QualityStatus] = None
    remarks: Optional[str] = None


class QualityInspectionResponse(BaseModel):
    id: uuid.UUID
    work_order_id: uuid.UUID
    inspector_id: Optional[uuid.UUID] = None
    inspected_quantity: int
    accepted_quantity: int
    rejected_quantity: int
    status: QualityStatus
    remarks: Optional[str] = None
    inspection_date: datetime
    created_at: datetime
    updated_at: datetime
    work_order_number: Optional[str] = None
    product_name: Optional[str] = None
    inspector_name: Optional[str] = None
    defects: List[QualityDefectResponse] = []

    class Config:
        from_attributes = True


# Summary Schema
class QualitySummaryResponse(BaseModel):
    total_inspections: int = 0
    pending: int = 0
    passed: int = 0
    failed: int = 0
    rework_required: int = 0
    total_rejected_quantity: int = 0
    total_defects: int = 0
