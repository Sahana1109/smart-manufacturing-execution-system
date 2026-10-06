import uuid
from datetime import date, datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product
from app.modules.production_planning.models import ProductionPlan
from app.modules.machines.models import Machine
from app.modules.employees.models import Employee
from app.modules.work_orders.models import WorkOrder, WorkOrderStatus


@pytest.mark.asyncio
async def test_01_start_valid_work_order(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    supervisor_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    sample_machine: Machine
):
    """Scenario 1: Start execution for a RELEASED work order."""
    # 1. Create Work Order
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 100,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    # 2. Assign machine and release to shop floor
    await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"assigned_machine_id": str(sample_machine.id)},
        headers=supervisor_token_headers
    )
    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "RELEASED"}, headers=manager_token_headers)

    # 3. Operator starts production execution
    start_res = await async_client.post(f"/api/v1/work-orders/{wo_id}/start", headers=operator_token_headers)
    assert start_res.status_code == 200
    data = start_res.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["actual_start_time"] is not None

    # Check machine status auto-synchronized to IN_USE
    m_res = await async_client.get(f"/api/v1/machines/{sample_machine.id}", headers=operator_token_headers)
    assert m_res.json()["status"] == "IN_USE"


@pytest.mark.asyncio
async def test_02_start_invalid_work_order_status(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 2: Starting a DRAFT work order returns 400 Bad Request."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 50,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    start_res = await async_client.post(f"/api/v1/work-orders/{wo_id}/start", headers=operator_token_headers)
    assert start_res.status_code == 400


@pytest.mark.asyncio
async def test_03_pause_and_resume_work_order(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    supervisor_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    sample_machine: Machine
):
    """Scenario 3: Pause and Resume execution workflow."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 80,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    await async_client.patch(f"/api/v1/work-orders/{wo_id}/assign", json={"assigned_machine_id": str(sample_machine.id)}, headers=supervisor_token_headers)
    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "RELEASED"}, headers=manager_token_headers)
    await async_client.post(f"/api/v1/work-orders/{wo_id}/start", headers=operator_token_headers)

    # 1. Pause execution
    pause_res = await async_client.post(
        f"/api/v1/work-orders/{wo_id}/pause",
        json={"reason": "Shift change brake"},
        headers=operator_token_headers
    )
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "PAUSED"

    m_res_paused = await async_client.get(f"/api/v1/machines/{sample_machine.id}", headers=operator_token_headers)
    assert m_res_paused.json()["status"] == "OPERATIONAL"

    # 2. Resume execution
    resume_res = await async_client.post(f"/api/v1/work-orders/{wo_id}/resume", headers=operator_token_headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["status"] == "IN_PROGRESS"

    m_res_resumed = await async_client.get(f"/api/v1/machines/{sample_machine.id}", headers=operator_token_headers)
    assert m_res_resumed.json()["status"] == "IN_USE"


@pytest.mark.asyncio
async def test_04_complete_production_execution(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    supervisor_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    sample_machine: Machine
):
    """Scenario 4: Complete production execution with produced quantity tracking."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 100,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    await async_client.patch(f"/api/v1/work-orders/{wo_id}/assign", json={"assigned_machine_id": str(sample_machine.id)}, headers=supervisor_token_headers)
    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "RELEASED"}, headers=manager_token_headers)
    await async_client.post(f"/api/v1/work-orders/{wo_id}/start", headers=operator_token_headers)

    # Complete production
    comp_res = await async_client.post(
        f"/api/v1/work-orders/{wo_id}/complete",
        json={"produced_quantity": 98, "notes": "98 PCS completed, 2 scrap"},
        headers=operator_token_headers
    )
    assert comp_res.status_code == 200
    data = comp_res.json()
    assert data["status"] == "COMPLETED"
    assert data["produced_quantity"] == 98
    assert data["actual_completion_time"] is not None
    assert data["progress_percentage"] == 98.0
    assert data["remaining_quantity"] == 2

    m_res = await async_client.get(f"/api/v1/machines/{sample_machine.id}", headers=operator_token_headers)
    assert m_res.json()["status"] == "OPERATIONAL"


@pytest.mark.asyncio
async def test_05_prevent_invalid_completion_quantity(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 5: Complete production with produced_quantity <= 0 returns 400 Bad Request."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 50,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "RELEASED"}, headers=manager_token_headers)
    await async_client.post(f"/api/v1/work-orders/{wo_id}/start", headers=operator_token_headers)

    comp_res = await async_client.post(
        f"/api/v1/work-orders/{wo_id}/complete",
        json={"produced_quantity": 0},
        headers=operator_token_headers
    )
    assert comp_res.status_code in (400, 422)


@pytest.mark.asyncio
async def test_06_record_and_list_downtime(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    sample_machine: Machine
):
    """Scenario 6: Record downtime event and list downtime log."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 120,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    now_dt = datetime.now(timezone.utc).isoformat()
    downtime_payload = {
        "work_order_id": wo_id,
        "machine_id": str(sample_machine.id),
        "start_time": now_dt,
        "duration_minutes": 45,
        "reason": "MACHINE_BREAKDOWN",
        "remarks": "Spindle overheat alert"
    }

    dt_res = await async_client.post(f"/api/v1/work-orders/{wo_id}/downtime", json=downtime_payload, headers=operator_token_headers)
    assert dt_res.status_code == 201
    dt_data = dt_res.json()
    assert dt_data["reason"] == "MACHINE_BREAKDOWN"
    assert dt_data["duration_minutes"] == 45

    # Fetch execution summary
    exec_res = await async_client.get(f"/api/v1/work-orders/{wo_id}/execution", headers=operator_token_headers)
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["total_downtime_minutes"] == 45
    assert len(exec_data["downtime_records"]) == 1


@pytest.mark.asyncio
async def test_07_invalid_downtime_duration(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 7: Negative downtime duration returns 400 Bad Request."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 50,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    downtime_payload = {
        "work_order_id": wo_id,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "duration_minutes": -15,
        "reason": "OTHER"
    }
    dt_res = await async_client.post(f"/api/v1/work-orders/{wo_id}/downtime", json=downtime_payload, headers=operator_token_headers)
    assert dt_res.status_code in (400, 422)
