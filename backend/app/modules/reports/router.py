from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import require_roles
from app.modules.reports.schemas import (
    DashboardSummaryResponse,
    ProductionReportResponse,
    QualityReportResponse,
    InventoryReportResponse,
    MachineReportResponse,
    OperatorReportResponse,
)
from app.modules.reports import service as reports_service

router = APIRouter()

REPORT_ROLES = [
    "ADMIN",
    "PRODUCTION_MANAGER",
    "SUPERVISOR",
    "QUALITY_INSPECTOR",
    "INVENTORY_MANAGER",
    "OPERATOR",
]


@router.get(
    "/dashboard",
    response_model=DashboardSummaryResponse,
    summary="Get consolidated management dashboard summary KPIs",
    dependencies=[Depends(require_roles(*REPORT_ROLES))],
)
async def get_dashboard_summary(
    from_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns consolidated high-level KPIs across Production, Quality, Inventory, Machines, and Operators.
    """
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_date cannot be after to_date",
        )
    return await reports_service.get_dashboard_summary(db, from_date=from_date, to_date=to_date)


@router.get(
    "/production",
    response_model=ProductionReportResponse,
    summary="Get production report summary",
    dependencies=[Depends(require_roles(*REPORT_ROLES))],
)
async def get_production_report(
    from_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns production execution report metrics (work orders count, status breakdown, quantity totals).
    """
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_date cannot be after to_date",
        )
    return await reports_service.get_production_report(db, from_date=from_date, to_date=to_date)


@router.get(
    "/quality",
    response_model=QualityReportResponse,
    summary="Get quality control report summary",
    dependencies=[Depends(require_roles(*REPORT_ROLES))],
)
async def get_quality_report(
    from_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns quality inspection report metrics (inspection breakdown, accepted/rejected quantities, defects).
    """
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_date cannot be after to_date",
        )
    return await reports_service.get_quality_report(db, from_date=from_date, to_date=to_date)


@router.get(
    "/inventory",
    response_model=InventoryReportResponse,
    summary="Get inventory report summary",
    dependencies=[Depends(require_roles(*REPORT_ROLES))],
)
async def get_inventory_report(
    db: AsyncSession = Depends(get_db),
):
    """
    Returns inventory stock levels, low-stock items, and recent movement audit trail.
    """
    return await reports_service.get_inventory_report(db)


@router.get(
    "/machines",
    response_model=MachineReportResponse,
    summary="Get machine status report summary",
    dependencies=[Depends(require_roles(*REPORT_ROLES))],
)
async def get_machine_report(
    db: AsyncSession = Depends(get_db),
):
    """
    Returns machine inventory status breakdown (operational, in use, maintenance, inactive).
    """
    return await reports_service.get_machine_report(db)


@router.get(
    "/operators",
    response_model=OperatorReportResponse,
    summary="Get operator / employee summary report",
    dependencies=[Depends(require_roles(*REPORT_ROLES))],
)
async def get_operator_report(
    db: AsyncSession = Depends(get_db),
):
    """
    Returns employee operational status summary (total, active, assigned, unassigned).
    """
    return await reports_service.get_operator_report(db)
