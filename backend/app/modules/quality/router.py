import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, require_roles
from app.modules.users.models import User
from app.modules.quality.models import QualityStatus
from app.modules.quality.schemas import (
    QualityInspectionCreate,
    QualityInspectionUpdate,
    QualityInspectionResponse,
    QualityDefectCreate,
    QualityDefectUpdate,
    QualityDefectResponse,
    QualitySummaryResponse,
)
from app.modules.quality import service as quality_service

router = APIRouter()

# Role Constants
READ_ROLES = ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR", "QUALITY_INSPECTOR", "OPERATOR", "INVENTORY_MANAGER"]
WRITE_ROLES = ["ADMIN", "PRODUCTION_MANAGER", "SUPERVISOR", "QUALITY_INSPECTOR"]


# --- Quality Summary Endpoint ---
@router.get(
    "/summary",
    response_model=QualitySummaryResponse,
    summary="Get aggregated quality inspection metrics for dashboard",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def get_quality_summary(
    db: AsyncSession = Depends(get_db),
):
    """
    Returns summary metrics: total inspections, counts by status, total rejected qty, and total defect count.
    """
    return await quality_service.get_quality_summary(db)


# --- Quality Inspection Endpoints ---
@router.post(
    "/inspections",
    response_model=QualityInspectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quality inspection for a completed work order",
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
async def create_inspection(
    payload: QualityInspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a quality inspection record. Only COMPLETED work orders can be inspected.
    """
    return await quality_service.create_quality_inspection(db, payload, current_user)


@router.get(
    "/inspections",
    response_model=List[QualityInspectionResponse],
    summary="List quality inspections with optional filtering",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def list_inspections(
    work_order_id: Optional[uuid.UUID] = Query(None, description="Filter by work order ID"),
    quality_status: Optional[QualityStatus] = Query(None, alias="status", description="Filter by quality status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists quality inspections sorted by creation date descending.
    """
    return await quality_service.list_quality_inspections(
        db, work_order_id=work_order_id, status=quality_status, skip=skip, limit=limit
    )


@router.get(
    "/inspections/{id}",
    response_model=QualityInspectionResponse,
    summary="Get quality inspection details by ID",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def get_inspection(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves detailed quality inspection including work order info and recorded defects.
    """
    return await quality_service.get_quality_inspection_by_id(db, id)


@router.patch(
    "/inspections/{id}",
    response_model=QualityInspectionResponse,
    summary="Update quality inspection properties",
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
async def update_inspection(
    id: uuid.UUID,
    payload: QualityInspectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates quantities, status, or remarks of an inspection.
    """
    return await quality_service.update_quality_inspection(db, id, payload, current_user)


# --- Quality Defect Endpoints ---
@router.post(
    "/inspections/{id}/defects",
    response_model=QualityDefectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a defect record to an inspection",
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
async def create_defect(
    id: uuid.UUID,
    payload: QualityDefectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Records a defect entry under an inspection.
    """
    return await quality_service.create_quality_defect(db, id, payload, current_user)


@router.get(
    "/inspections/{id}/defects",
    response_model=List[QualityDefectResponse],
    summary="List defects for an inspection",
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
async def list_defects(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Lists all defects associated with an inspection.
    """
    return await quality_service.list_quality_defects(db, id)


@router.patch(
    "/defects/{id}",
    response_model=QualityDefectResponse,
    summary="Update a quality defect entry",
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
async def update_defect(
    id: uuid.UUID,
    payload: QualityDefectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates a defect's type, severity, description, quantity, or remarks.
    """
    return await quality_service.update_quality_defect(db, id, payload, current_user)


@router.delete(
    "/defects/{id}",
    summary="Delete a quality defect entry",
    dependencies=[Depends(require_roles(*WRITE_ROLES))],
)
async def delete_defect(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Removes a quality defect record.
    """
    return await quality_service.delete_quality_defect(db, id, current_user)
