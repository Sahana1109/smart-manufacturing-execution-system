import uuid
from datetime import date, timedelta
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.products.models import Product
from app.modules.production_planning.models import ProductionPlan
from app.modules.machines.models import Machine
from app.modules.employees.models import Employee
from app.modules.work_orders.models import WorkOrder, WorkOrderStatus
from app.modules.audit_logs.models import AuditLog


@pytest.mark.asyncio
async def test_01_create_work_order_successfully(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 1: Production Manager creates valid Work Order."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 100,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=5)),
        "priority": "HIGH",
        "notes": "First shift execution batch"
    }
    response = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["work_order_number"].startswith("WO-")
    assert data["planned_quantity"] == 100
    assert data["status"] == "DRAFT"
    assert data["production_plan_id"] == str(sample_plan.id)


@pytest.mark.asyncio
async def test_02_duplicate_work_order_number(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 2: Duplicate custom work order number returns 409 Conflict."""
    payload = {
        "work_order_number": "WO-CUSTOM-999",
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res1 = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    assert res1.status_code == 201

    res2 = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    assert res2.status_code == 409


@pytest.mark.asyncio
async def test_03_invalid_quantity(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 3: Quantity <= 0 returns 400/422 validation error."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 0,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    response = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_04_invalid_dates(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 4: start_date > due_date returns 422/400 validation error."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today() + timedelta(days=10)),
        "due_date": str(date.today())
    }
    response = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_05_non_existent_production_plan(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 5: Non-existent production plan ID returns 404."""
    payload = {
        "production_plan_id": str(uuid.uuid4()),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    response = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_06_inactive_product(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    db_session: AsyncSession
):
    """Scenario 6: Inactive product returns 400 Bad Request."""
    inactive_prod = Product(
        product_code="INACTIVE-WO-PRD",
        name="Inactive Product for WO",
        unit_of_measure="PCS",
        is_active=False
    )
    db_session.add(inactive_prod)
    await db_session.commit()

    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(inactive_prod.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    response = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_07_successful_status_transition(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 7: State machine transitions DRAFT -> RELEASED -> IN_PROGRESS -> COMPLETED -> CLOSED."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    # 1. DRAFT -> RELEASED
    r1 = await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "RELEASED"}, headers=manager_token_headers)
    assert r1.status_code == 200
    assert r1.json()["status"] == "RELEASED"

    # 2. RELEASED -> IN_PROGRESS
    r2 = await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "IN_PROGRESS"}, headers=manager_token_headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "IN_PROGRESS"

    # 3. IN_PROGRESS -> COMPLETED
    r3 = await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "COMPLETED"}, headers=manager_token_headers)
    assert r3.status_code == 200
    assert r3.json()["status"] == "COMPLETED"

    # 4. COMPLETED -> CLOSED
    r4 = await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "CLOSED"}, headers=manager_token_headers)
    assert r4.status_code == 200
    assert r4.json()["status"] == "CLOSED"


@pytest.mark.asyncio
async def test_08_invalid_status_transition(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 8: Invalid transition (DRAFT -> COMPLETED) returns 400 Bad Request."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    r_invalid = await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "COMPLETED"}, headers=manager_token_headers)
    assert r_invalid.status_code == 400


@pytest.mark.asyncio
async def test_09_pause_work_order(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 9: Transition IN_PROGRESS -> PAUSED."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "RELEASED"}, headers=manager_token_headers)
    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "IN_PROGRESS"}, headers=manager_token_headers)

    pause_res = await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "PAUSED"}, headers=manager_token_headers)
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "PAUSED"


@pytest.mark.asyncio
async def test_10_resume_work_order(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 10: Transition PAUSED -> IN_PROGRESS."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "RELEASED"}, headers=manager_token_headers)
    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "IN_PROGRESS"}, headers=manager_token_headers)
    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "PAUSED"}, headers=manager_token_headers)

    resume_res = await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "IN_PROGRESS"}, headers=manager_token_headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_11_complete_work_order(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 11: Transition IN_PROGRESS -> COMPLETED."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "RELEASED"}, headers=manager_token_headers)
    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "IN_PROGRESS"}, headers=manager_token_headers)

    comp_res = await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "COMPLETED"}, headers=manager_token_headers)
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_12_cancel_work_order(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 12: Cancelling work order transitions status to CANCELLED."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    cancel_res = await async_client.post(f"/api/v1/work-orders/{wo_id}/cancel", headers=manager_token_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_13_unauthorized_creation(async_client: AsyncClient, sample_plan: ProductionPlan, sample_product: Product):
    """Scenario 13: Unauthenticated creation returns 401."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload)
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_14_unauthorized_update(
    async_client: AsyncClient,
    operator_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 14: Operator creation returns 403 Forbidden."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=operator_token_headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_15_unauthorized_cancellation(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 15: Operator cancellation returns 403 Forbidden."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    cancel_res = await async_client.post(f"/api/v1/work-orders/{wo_id}/cancel", headers=operator_token_headers)
    assert cancel_res.status_code == 403


@pytest.mark.asyncio
async def test_16_work_order_listing(
    async_client: AsyncClient,
    manager_token_headers: dict
):
    """Scenario 16: Listing work orders returns paginated object."""
    res = await async_client.get("/api/v1/work-orders", headers=manager_token_headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_17_pagination(
    async_client: AsyncClient,
    manager_token_headers: dict
):
    """Scenario 17: Pagination query parameters."""
    res = await async_client.get("/api/v1/work-orders?page=1&limit=5", headers=manager_token_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["limit"] == 5


@pytest.mark.asyncio
async def test_18_status_filtering(
    async_client: AsyncClient,
    manager_token_headers: dict
):
    """Scenario 18: Filter work orders by status."""
    res = await async_client.get("/api/v1/work-orders?status=RELEASED", headers=manager_token_headers)
    assert res.status_code == 200
    assert isinstance(res.json()["items"], list)


@pytest.mark.asyncio
async def test_19_priority_filtering(
    async_client: AsyncClient,
    manager_token_headers: dict
):
    """Scenario 19: Filter work orders by priority."""
    res = await async_client.get("/api/v1/work-orders?priority=HIGH", headers=manager_token_headers)
    assert res.status_code == 200
    assert isinstance(res.json()["items"], list)


@pytest.mark.asyncio
async def test_20_search(
    async_client: AsyncClient,
    manager_token_headers: dict
):
    """Scenario 20: Search work orders by query term."""
    res = await async_client.get("/api/v1/work-orders?search=WO-", headers=manager_token_headers)
    assert res.status_code == 200
    assert isinstance(res.json()["items"], list)


@pytest.mark.asyncio
async def test_21_production_plan_filtering(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan
):
    """Scenario 21: Filter work orders by production_plan_id."""
    res = await async_client.get(f"/api/v1/work-orders?production_plan_id={sample_plan.id}", headers=manager_token_headers)
    assert res.status_code == 200
    assert isinstance(res.json()["items"], list)


@pytest.mark.asyncio
async def test_22_audit_log_creation(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    db_session: AsyncSession
):
    """Scenario 22: Work Order creation records AuditLog in database."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 80,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    create_res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = create_res.json()["id"]

    stmt = select(AuditLog).where(AuditLog.entity_id == str(wo_id))
    res = await db_session.execute(stmt)
    logs = res.scalars().all()
    assert len(logs) > 0
    assert logs[0].action == "WORK_ORDER_CREATED"


@pytest.mark.asyncio
async def test_23_machine_assignment(
    async_client: AsyncClient,
    supervisor_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    sample_machine: Machine
):
    """Scenario 23: Supervisor assigns machine to work order."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 80,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    assign_payload = {"assigned_machine_id": str(sample_machine.id)}
    assign_res = await async_client.patch(f"/api/v1/work-orders/{wo_id}/assign", json=assign_payload, headers=supervisor_token_headers)
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_machine_id"] == str(sample_machine.id)


@pytest.mark.asyncio
async def test_24_employee_assignment(
    async_client: AsyncClient,
    supervisor_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    sample_employee: Employee
):
    """Scenario 24: Supervisor assigns employee operator to work order."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 80,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    assign_payload = {"assigned_employee_id": str(sample_employee.id)}
    assign_res = await async_client.patch(f"/api/v1/work-orders/{wo_id}/assign", json=assign_payload, headers=supervisor_token_headers)
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_employee_id"] == str(sample_employee.id)


@pytest.mark.asyncio
async def test_25_work_order_details(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 25: Fetching work order details returns full pre-loaded object."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 80,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    get_res = await async_client.get(f"/api/v1/work-orders/{wo_id}", headers=manager_token_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == wo_id


@pytest.mark.asyncio
async def test_26_operator_status_transition_restriction(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 26: Operator role is restricted to execution-only status transitions (403 for RELEASED/CLOSED)."""
    payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    res = await async_client.post("/api/v1/work-orders", json=payload, headers=manager_token_headers)
    wo_id = res.json()["id"]

    # Operator trying DRAFT -> RELEASED should receive 403 Forbidden
    r_forbidden = await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/status",
        json={"status": "RELEASED"},
        headers=operator_token_headers
    )
    assert r_forbidden.status_code == 403
