from datetime import date, datetime, time
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_

from app.modules.work_orders.models import WorkOrder, WorkOrderStatus
from app.modules.quality.models import QualityInspection, QualityDefect, QualityStatus
from app.modules.inventory.models import Material, InventoryStock, StockMovement
from app.modules.machines.models import Machine
from app.modules.employees.models import Employee
from app.modules.inventory.service import get_low_stock_materials, list_stock_movements
from app.modules.reports.schemas import (
    ProductionReportResponse,
    QualityReportResponse,
    InventoryReportResponse,
    MachineReportResponse,
    OperatorReportResponse,
    DashboardSummaryResponse,
)


async def get_production_report(
    db: AsyncSession,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> ProductionReportResponse:
    """
    Computes production KPI metrics: total work orders, status breakdown, completion percentage,
    planned quantity, and produced quantity.
    """
    query = select(WorkOrder)

    if from_date:
        from_dt = datetime.combine(from_date, time.min)
        query = query.where(WorkOrder.created_at >= from_dt)
    if to_date:
        to_dt = datetime.combine(to_date, time.max)
        query = query.where(WorkOrder.created_at <= to_dt)

    result = await db.execute(query)
    work_orders = result.scalars().all()

    total_work_orders = len(work_orders)
    pending = 0
    in_progress = 0
    paused = 0
    completed = 0
    closed = 0
    cancelled = 0
    total_planned_quantity = 0
    total_produced_quantity = 0

    for wo in work_orders:
        total_planned_quantity += wo.planned_quantity or 0
        total_produced_quantity += wo.produced_quantity or 0

        st = wo.status.value if hasattr(wo.status, 'value') else str(wo.status)
        if st in (WorkOrderStatus.DRAFT.value, WorkOrderStatus.RELEASED.value):
            pending += 1
        elif st == WorkOrderStatus.IN_PROGRESS.value:
            in_progress += 1
        elif st == WorkOrderStatus.PAUSED.value:
            paused += 1
        elif st == WorkOrderStatus.COMPLETED.value:
            completed += 1
        elif st == WorkOrderStatus.CLOSED.value:
            closed += 1
        elif st == WorkOrderStatus.CANCELLED.value:
            cancelled += 1

    completion_percentage = (
        round((completed / total_work_orders) * 100.0, 1)
        if total_work_orders > 0
        else 0.0
    )

    return ProductionReportResponse(
        total_work_orders=total_work_orders,
        pending=pending,
        in_progress=in_progress,
        paused=paused,
        completed=completed,
        closed=closed,
        cancelled=cancelled,
        completion_percentage=completion_percentage,
        total_planned_quantity=total_planned_quantity,
        total_produced_quantity=total_produced_quantity,
    )


async def get_quality_report(
    db: AsyncSession,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> QualityReportResponse:
    """
    Computes quality KPI metrics: total inspections, inspection status breakdown, inspected, accepted,
    rejected quantities, and total defect count.
    """
    insp_query = select(QualityInspection)

    if from_date:
        from_dt = datetime.combine(from_date, time.min)
        insp_query = insp_query.where(QualityInspection.created_at >= from_dt)
    if to_date:
        to_dt = datetime.combine(to_date, time.max)
        insp_query = insp_query.where(QualityInspection.created_at <= to_dt)

    result = await db.execute(insp_query)
    inspections = result.scalars().all()

    total_inspections = len(inspections)
    pending = 0
    passed = 0
    failed = 0
    rework_required = 0
    total_inspected_quantity = 0
    total_accepted_quantity = 0
    total_rejected_quantity = 0

    for insp in inspections:
        total_inspected_quantity += insp.inspected_quantity or 0
        total_accepted_quantity += insp.accepted_quantity or 0
        total_rejected_quantity += insp.rejected_quantity or 0

        st = insp.status.value if hasattr(insp.status, 'value') else str(insp.status)
        if st == QualityStatus.PENDING.value:
            pending += 1
        elif st == QualityStatus.PASSED.value:
            passed += 1
        elif st == QualityStatus.FAILED.value:
            failed += 1
        elif st == QualityStatus.REWORK_REQUIRED.value:
            rework_required += 1

    # Total defect count
    defect_query = select(func.coalesce(func.sum(QualityDefect.quantity), 0))
    if from_date or to_date:
        defect_query = defect_query.join(QualityInspection)
        if from_date:
            from_dt = datetime.combine(from_date, time.min)
            defect_query = defect_query.where(QualityInspection.created_at >= from_dt)
        if to_date:
            to_dt = datetime.combine(to_date, time.max)
            defect_query = defect_query.where(QualityInspection.created_at <= to_dt)

    defect_res = await db.execute(defect_query)
    total_defects = defect_res.scalar() or 0

    return QualityReportResponse(
        total_inspections=total_inspections,
        pending=pending,
        passed=passed,
        failed=failed,
        rework_required=rework_required,
        total_inspected_quantity=total_inspected_quantity,
        total_accepted_quantity=total_accepted_quantity,
        total_rejected_quantity=total_rejected_quantity,
        total_defects=int(total_defects),
    )


async def get_inventory_report(
    db: AsyncSession,
) -> InventoryReportResponse:
    """
    Computes inventory KPI metrics: total materials, stock totals, low stock count, low stock list,
    and recent movements.
    """
    # Total materials
    mat_res = await db.execute(select(func.count(Material.id)))
    total_materials = mat_res.scalar() or 0

    # Stock items & totals
    stock_res = await db.execute(select(InventoryStock))
    stocks = stock_res.scalars().all()

    total_stock_items = len(stocks)
    total_quantity = sum(s.quantity or 0 for s in stocks)
    total_reserved_quantity = sum(s.reserved_quantity or 0 for s in stocks)
    total_available_quantity = sum(s.available_quantity for s in stocks)

    # Low stock list & count
    low_stock_materials = await get_low_stock_materials(db)
    low_stock_count = len(low_stock_materials)

    # Recent movements
    recent_movements = await list_stock_movements(db, limit=10)

    return InventoryReportResponse(
        total_materials=total_materials,
        total_stock_items=total_stock_items,
        total_quantity=total_quantity,
        total_reserved_quantity=total_reserved_quantity,
        total_available_quantity=total_available_quantity,
        low_stock_count=low_stock_count,
        low_stock_materials=low_stock_materials,
        recent_movements=recent_movements,
    )


async def get_machine_report(
    db: AsyncSession,
) -> MachineReportResponse:
    """
    Computes machine status breakdown metrics.
    """
    res = await db.execute(select(Machine))
    machines = res.scalars().all()

    total_machines = len(machines)
    operational = 0
    in_use = 0
    maintenance = 0
    inactive = 0

    for m in machines:
        if not m.is_active:
            inactive += 1
        else:
            st = (m.status or "").upper()
            if st == "OPERATIONAL":
                operational += 1
            elif st == "IN_USE":
                in_use += 1
            elif st in ("MAINTENANCE", "UNDER_MAINTENANCE"):
                maintenance += 1
            elif st == "INACTIVE":
                inactive += 1
            else:
                operational += 1

    return MachineReportResponse(
        total_machines=total_machines,
        operational=operational,
        in_use=in_use,
        maintenance=maintenance,
        inactive=inactive,
    )


async def get_operator_report(
    db: AsyncSession,
) -> OperatorReportResponse:
    """
    Computes employee / operator summary metrics.
    """
    res = await db.execute(select(Employee))
    employees = res.scalars().all()

    total_operators = len(employees)
    active_operators = sum(1 for e in employees if e.is_active)

    # Count employees assigned to active Work Orders (RELEASED, IN_PROGRESS, PAUSED)
    assigned_res = await db.execute(
        select(func.count(func.distinct(WorkOrder.assigned_employee_id))).where(
            and_(
                WorkOrder.assigned_employee_id.isnot(None),
                WorkOrder.status.in_([
                    WorkOrderStatus.RELEASED,
                    WorkOrderStatus.IN_PROGRESS,
                    WorkOrderStatus.PAUSED,
                ]),
            )
        )
    )
    assigned_operators = assigned_res.scalar() or 0
    unassigned_operators = max(0, active_operators - assigned_operators)

    return OperatorReportResponse(
        total_operators=total_operators,
        active_operators=active_operators,
        assigned_operators=assigned_operators,
        unassigned_operators=unassigned_operators,
    )


async def get_dashboard_summary(
    db: AsyncSession,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> DashboardSummaryResponse:
    """
    Consolidates production, quality, inventory, machine, and operator KPI reports into a single response.
    """
    production = await get_production_report(db, from_date=from_date, to_date=to_date)
    quality = await get_quality_report(db, from_date=from_date, to_date=to_date)
    inventory = await get_inventory_report(db)
    machines = await get_machine_report(db)
    operators = await get_operator_report(db)

    return DashboardSummaryResponse(
        production=production,
        quality=quality,
        inventory=inventory,
        machines=machines,
        operators=operators,
    )
