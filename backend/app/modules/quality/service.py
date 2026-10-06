import uuid
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.modules.quality.models import QualityInspection, QualityDefect, QualityStatus
from app.modules.quality.schemas import (
    QualityInspectionCreate,
    QualityInspectionUpdate,
    QualityInspectionResponse,
    QualityDefectCreate,
    QualityDefectUpdate,
    QualityDefectResponse,
    QualitySummaryResponse,
)
from app.modules.work_orders.models import WorkOrder, WorkOrderStatus
from app.modules.users.models import User
from app.modules.audit_logs.service import log_audit_event

logger = logging.getLogger(__name__)


def _build_inspection_response(inspection: QualityInspection) -> QualityInspectionResponse:
    wo_number = inspection.work_order.work_order_number if inspection.work_order else None
    product_name = inspection.work_order.product.name if inspection.work_order and inspection.work_order.product else None
    inspector_name = (
        f"{inspection.inspector.first_name} {inspection.inspector.last_name}".strip()
        if inspection.inspector and (inspection.inspector.first_name or inspection.inspector.last_name)
        else (inspection.inspector.email if inspection.inspector else None)
    )

    defect_responses = [
        QualityDefectResponse.model_validate(d) for d in (inspection.defects or [])
    ]

    return QualityInspectionResponse(
        id=inspection.id,
        work_order_id=inspection.work_order_id,
        inspector_id=inspection.inspector_id,
        inspected_quantity=inspection.inspected_quantity,
        accepted_quantity=inspection.accepted_quantity,
        rejected_quantity=inspection.rejected_quantity,
        status=inspection.status,
        remarks=inspection.remarks,
        inspection_date=inspection.inspection_date,
        created_at=inspection.created_at,
        updated_at=inspection.updated_at,
        work_order_number=wo_number,
        product_name=product_name,
        inspector_name=inspector_name,
        defects=defect_responses,
    )


async def create_quality_inspection(
    db: AsyncSession,
    payload: QualityInspectionCreate,
    current_user: User,
) -> QualityInspectionResponse:
    """
    Creates a new quality inspection for a COMPLETED work order.
    """
    # 1. Validate Work Order exists
    stmt = select(WorkOrder).options(selectinload(WorkOrder.product)).where(WorkOrder.id == payload.work_order_id)
    res = await db.execute(stmt)
    work_order = res.scalar_one_or_none()
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Work order with ID {payload.work_order_id} not found")

    # 2. Validate Work Order status is COMPLETED
    if work_order.status != WorkOrderStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only completed work orders can undergo quality inspection")

    # 3. Validate quantities
    if payload.inspected_quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inspected quantity cannot be negative")
    if payload.accepted_quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accepted quantity cannot be negative")
    if payload.rejected_quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rejected quantity cannot be negative")

    if (payload.accepted_quantity + payload.rejected_quantity) > payload.inspected_quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accepted plus rejected quantity cannot exceed inspected quantity")

    # 4. Create inspection entity
    inspection = QualityInspection(
        work_order_id=payload.work_order_id,
        inspector_id=current_user.id,
        inspected_quantity=payload.inspected_quantity,
        accepted_quantity=payload.accepted_quantity,
        rejected_quantity=payload.rejected_quantity,
        status=payload.status,
        remarks=payload.remarks,
    )
    db.add(inspection)
    await db.flush()

    # 5. Audit Log
    await log_audit_event(
        db,
        action="QUALITY_INSPECTION_CREATED",
        entity_type="QualityInspection",
        entity_id=str(inspection.id),
        user_id=current_user.id,
        details={
            "work_order_id": str(payload.work_order_id),
            "status": str(payload.status),
            "inspected": payload.inspected_quantity,
            "accepted": payload.accepted_quantity,
            "rejected": payload.rejected_quantity,
        }
    )

    await db.commit()

    # Re-fetch with relationships
    stmt_full = (
        select(QualityInspection)
        .options(
            selectinload(QualityInspection.work_order).selectinload(WorkOrder.product),
            selectinload(QualityInspection.inspector),
            selectinload(QualityInspection.defects),
        )
        .where(QualityInspection.id == inspection.id)
    )
    res_full = await db.execute(stmt_full)
    full_inspection = res_full.scalar_one()

    return _build_inspection_response(full_inspection)


async def get_quality_inspection_by_id(
    db: AsyncSession,
    inspection_id: uuid.UUID,
) -> QualityInspectionResponse:
    """
    Retrieves quality inspection details by ID.
    """
    stmt = (
        select(QualityInspection)
        .options(
            selectinload(QualityInspection.work_order).selectinload(WorkOrder.product),
            selectinload(QualityInspection.inspector),
            selectinload(QualityInspection.defects),
        )
        .where(QualityInspection.id == inspection_id)
    )
    res = await db.execute(stmt)
    inspection = res.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quality inspection with ID {inspection_id} not found")

    return _build_inspection_response(inspection)


async def list_quality_inspections(
    db: AsyncSession,
    work_order_id: Optional[uuid.UUID] = None,
    status: Optional[QualityStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[QualityInspectionResponse]:
    """
    Lists quality inspections with optional filtering.
    """
    stmt = (
        select(QualityInspection)
        .options(
            selectinload(QualityInspection.work_order).selectinload(WorkOrder.product),
            selectinload(QualityInspection.inspector),
            selectinload(QualityInspection.defects),
        )
        .order_by(desc(QualityInspection.created_at))
    )

    if work_order_id is not None:
        stmt = stmt.where(QualityInspection.work_order_id == work_order_id)
    if status is not None:
        stmt = stmt.where(QualityInspection.status == status)

    stmt = stmt.offset(skip).limit(limit)
    res = await db.execute(stmt)
    inspections = res.scalars().all()

    return [_build_inspection_response(ins) for ins in inspections]


async def update_quality_inspection(
    db: AsyncSession,
    inspection_id: uuid.UUID,
    payload: QualityInspectionUpdate,
    current_user: User,
) -> QualityInspectionResponse:
    """
    Updates an existing quality inspection entity.
    """
    stmt = (
        select(QualityInspection)
        .options(
            selectinload(QualityInspection.work_order).selectinload(WorkOrder.product),
            selectinload(QualityInspection.inspector),
            selectinload(QualityInspection.defects),
        )
        .where(QualityInspection.id == inspection_id)
    )
    res = await db.execute(stmt)
    inspection = res.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quality inspection with ID {inspection_id} not found")

    inspected = payload.inspected_quantity if payload.inspected_quantity is not None else inspection.inspected_quantity
    accepted = payload.accepted_quantity if payload.accepted_quantity is not None else inspection.accepted_quantity
    rejected = payload.rejected_quantity if payload.rejected_quantity is not None else inspection.rejected_quantity

    if inspected < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inspected quantity cannot be negative")
    if accepted < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accepted quantity cannot be negative")
    if rejected < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rejected quantity cannot be negative")

    if (accepted + rejected) > inspected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accepted plus rejected quantity cannot exceed inspected quantity")

    if payload.inspected_quantity is not None:
        inspection.inspected_quantity = payload.inspected_quantity
    if payload.accepted_quantity is not None:
        inspection.accepted_quantity = payload.accepted_quantity
    if payload.rejected_quantity is not None:
        inspection.rejected_quantity = payload.rejected_quantity
    if payload.status is not None:
        inspection.status = payload.status
    if payload.remarks is not None:
        inspection.remarks = payload.remarks

    await log_audit_event(
        db,
        action="QUALITY_INSPECTION_UPDATED",
        entity_type="QualityInspection",
        entity_id=str(inspection.id),
        user_id=current_user.id,
        details={
            "status": str(inspection.status),
            "inspected": inspection.inspected_quantity,
            "accepted": inspection.accepted_quantity,
            "rejected": inspection.rejected_quantity,
        }
    )

    await db.commit()
    await db.refresh(inspection)

    return _build_inspection_response(inspection)


async def create_quality_defect(
    db: AsyncSession,
    inspection_id: uuid.UUID,
    payload: QualityDefectCreate,
    current_user: User,
) -> QualityDefectResponse:
    """
    Creates a defect record linked to an inspection.
    """
    stmt = select(QualityInspection).where(QualityInspection.id == inspection_id)
    res = await db.execute(stmt)
    inspection = res.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quality inspection with ID {inspection_id} not found")

    if payload.quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Defect quantity cannot be negative")

    defect = QualityDefect(
        inspection_id=inspection_id,
        defect_type=payload.defect_type,
        severity=payload.severity,
        description=payload.description,
        quantity=payload.quantity,
        remarks=payload.remarks,
    )
    db.add(defect)
    await db.flush()

    await log_audit_event(
        db,
        action="QUALITY_DEFECT_CREATED",
        entity_type="QualityDefect",
        entity_id=str(defect.id),
        user_id=current_user.id,
        details={
            "inspection_id": str(inspection_id),
            "defect_type": str(payload.defect_type),
            "severity": str(payload.severity),
            "quantity": payload.quantity,
        }
    )

    await db.commit()
    await db.refresh(defect)

    return QualityDefectResponse.model_validate(defect)


async def list_quality_defects(
    db: AsyncSession,
    inspection_id: uuid.UUID,
) -> List[QualityDefectResponse]:
    """
    Lists all defect records for an inspection.
    """
    stmt = select(QualityInspection).where(QualityInspection.id == inspection_id)
    res = await db.execute(stmt)
    inspection = res.scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quality inspection with ID {inspection_id} not found")

    stmt_defects = (
        select(QualityDefect)
        .where(QualityDefect.inspection_id == inspection_id)
        .order_by(desc(QualityDefect.created_at))
    )
    res_defects = await db.execute(stmt_defects)
    defects = res_defects.scalars().all()

    return [QualityDefectResponse.model_validate(d) for d in defects]


async def update_quality_defect(
    db: AsyncSession,
    defect_id: uuid.UUID,
    payload: QualityDefectUpdate,
    current_user: User,
) -> QualityDefectResponse:
    """
    Updates a quality defect record.
    """
    stmt = select(QualityDefect).where(QualityDefect.id == defect_id)
    res = await db.execute(stmt)
    defect = res.scalar_one_or_none()
    if not defect:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quality defect with ID {defect_id} not found")

    if payload.quantity is not None:
        if payload.quantity < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Defect quantity cannot be negative")
        defect.quantity = payload.quantity

    if payload.defect_type is not None:
        defect.defect_type = payload.defect_type
    if payload.severity is not None:
        defect.severity = payload.severity
    if payload.description is not None:
        defect.description = payload.description
    if payload.remarks is not None:
        defect.remarks = payload.remarks

    await log_audit_event(
        db,
        action="QUALITY_DEFECT_UPDATED",
        entity_type="QualityDefect",
        entity_id=str(defect.id),
        user_id=current_user.id,
        details={
            "defect_type": str(defect.defect_type),
            "severity": str(defect.severity),
            "quantity": defect.quantity,
        }
    )

    await db.commit()
    await db.refresh(defect)

    return QualityDefectResponse.model_validate(defect)


async def delete_quality_defect(
    db: AsyncSession,
    defect_id: uuid.UUID,
    current_user: User,
) -> dict:
    """
    Deletes a quality defect record.
    """
    stmt = select(QualityDefect).where(QualityDefect.id == defect_id)
    res = await db.execute(stmt)
    defect = res.scalar_one_or_none()
    if not defect:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quality defect with ID {defect_id} not found")

    await db.delete(defect)

    await log_audit_event(
        db,
        action="QUALITY_DEFECT_DELETED",
        entity_type="QualityDefect",
        entity_id=str(defect_id),
        user_id=current_user.id,
        details={"inspection_id": str(defect.inspection_id)}
    )

    await db.commit()

    return {"message": f"Quality defect {defect_id} deleted successfully"}


async def get_quality_summary(db: AsyncSession) -> QualitySummaryResponse:
    """
    Provides aggregated metrics for Quality Inspection Dashboard.
    """
    # Total inspections & counts by status
    stmt_counts = select(
        QualityInspection.status,
        func.count(QualityInspection.id)
    ).group_by(QualityInspection.status)

    res_counts = await db.execute(stmt_counts)
    status_map = {row[0]: row[1] for row in res_counts.all()}

    pending = status_map.get(QualityStatus.PENDING, 0)
    passed = status_map.get(QualityStatus.PASSED, 0)
    failed = status_map.get(QualityStatus.FAILED, 0)
    rework = status_map.get(QualityStatus.REWORK_REQUIRED, 0)
    total_inspections = pending + passed + failed + rework

    # Total rejected quantity
    stmt_rejected = select(func.coalesce(func.sum(QualityInspection.rejected_quantity), 0))
    res_rejected = await db.execute(stmt_rejected)
    total_rejected = res_rejected.scalar() or 0

    # Total defects (sum of defect quantities)
    stmt_defects = select(func.coalesce(func.sum(QualityDefect.quantity), 0))
    res_defects = await db.execute(stmt_defects)
    total_defects = res_defects.scalar() or 0

    return QualitySummaryResponse(
        total_inspections=total_inspections,
        pending=pending,
        passed=passed,
        failed=failed,
        rework_required=rework,
        total_rejected_quantity=total_rejected,
        total_defects=total_defects,
    )
