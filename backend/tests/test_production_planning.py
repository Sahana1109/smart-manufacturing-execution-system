import uuid
from datetime import date, timedelta
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.products.models import Product
from app.modules.production_planning.models import ProductionPlan, ProductionPlanStatus, ProductionPlanPriority
from app.modules.audit_logs.models import AuditLog
from app.modules.users.models import User


@pytest.mark.asyncio
async def test_01_create_production_plan_successfully(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 1: Production Manager creates valid plan."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 150,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=7)),
        "priority": "HIGH",
        "notes": "Urgent order for client A"
    }
    response = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["plan_number"].startswith("PP-")
    assert data["planned_quantity"] == 150
    assert data["priority"] == "HIGH"
    assert data["status"] == "DRAFT"


@pytest.mark.asyncio
async def test_02_create_plan_unauthenticated(async_client: AsyncClient, sample_product: Product):
    """Scenario 2: Reject plan creation without authentication (401)."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 100,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=5))
    }
    response = await async_client.post("/api/v1/production-plans", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_03_create_plan_unauthorized_role(
    async_client: AsyncClient,
    operator_token_headers: dict,
    sample_product: Product
):
    """Scenario 3: Reject plan creation by OPERATOR role (403)."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 100,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=5))
    }
    response = await async_client.post("/api/v1/production-plans", json=payload, headers=operator_token_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_04_invalid_product(async_client: AsyncClient, manager_token_headers: dict):
    """Scenario 4: Non-existent product ID returns 404."""
    payload = {
        "product_id": str(uuid.uuid4()),
        "planned_quantity": 100,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=5))
    }
    response = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_05_inactive_product(
    async_client: AsyncClient,
    manager_token_headers: dict,
    db_session: AsyncSession
):
    """Scenario 5: Scheduling plan for inactive product returns 400."""
    inactive_prod = Product(
        product_code="INACTIVE-PRD",
        name="Inactive Product",
        unit_of_measure="PCS",
        is_active=False
    )
    db_session.add(inactive_prod)
    await db_session.commit()

    payload = {
        "product_id": str(inactive_prod.id),
        "planned_quantity": 100,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=5))
    }
    response = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_06_invalid_quantity(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 6: Quantity <= 0 returns 422 validation error."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 0,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=5))
    }
    response = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_07_invalid_date_range(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 7: start_date > due_date returns 400 Bad Request."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 100,
        "start_date": str(date.today() + timedelta(days=10)),
        "due_date": str(date.today())
    }
    response = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_08_duplicate_plan_number(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 8: Duplicate plan number returns 409 Conflict."""
    payload = {
        "plan_number": "PP-DUP-001",
        "product_id": str(sample_product.id),
        "planned_quantity": 100,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=5))
    }
    res1 = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    assert res1.status_code == 201

    res2 = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    assert res2.status_code == 409


@pytest.mark.asyncio
async def test_09_get_production_plan(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 9: Fetch plan by ID returns plan details."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=2))
    }
    create_res = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    plan_id = create_res.json()["id"]

    get_res = await async_client.get(f"/api/v1/production-plans/{plan_id}", headers=manager_token_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == plan_id


@pytest.mark.asyncio
async def test_10_list_production_plans(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 10: Listing plans returns paginated payload."""
    response = await async_client.get("/api/v1/production-plans", headers=manager_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_11_update_production_plan(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 11: Updating plan quantity and notes returns updated object."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=2))
    }
    create_res = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    plan_id = create_res.json()["id"]

    update_payload = {"planned_quantity": 250, "notes": "Updated batch size"}
    update_res = await async_client.put(f"/api/v1/production-plans/{plan_id}", json=update_payload, headers=manager_token_headers)
    assert update_res.status_code == 200
    assert update_res.json()["planned_quantity"] == 250


@pytest.mark.asyncio
async def test_12_invalid_status_transition(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 12: Invalid transition (DRAFT -> COMPLETED) returns 400 Bad Request."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=2))
    }
    create_res = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    plan_id = create_res.json()["id"]

    status_res = await async_client.patch(f"/api/v1/production-plans/{plan_id}/status", json={"status": "COMPLETED"}, headers=manager_token_headers)
    assert status_res.status_code == 400


@pytest.mark.asyncio
async def test_13_valid_status_transition(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 13: Valid state transitions DRAFT -> PLANNED -> IN_PROGRESS -> COMPLETED."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=2))
    }
    create_res = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    plan_id = create_res.json()["id"]

    # 1. DRAFT -> PLANNED
    res1 = await async_client.patch(f"/api/v1/production-plans/{plan_id}/status", json={"status": "PLANNED"}, headers=manager_token_headers)
    assert res1.status_code == 200
    assert res1.json()["status"] == "PLANNED"

    # 2. PLANNED -> IN_PROGRESS
    res2 = await async_client.patch(f"/api/v1/production-plans/{plan_id}/status", json={"status": "IN_PROGRESS"}, headers=manager_token_headers)
    assert res2.status_code == 200
    assert res2.json()["status"] == "IN_PROGRESS"

    # 3. IN_PROGRESS -> COMPLETED
    res3 = await async_client.patch(f"/api/v1/production-plans/{plan_id}/status", json={"status": "COMPLETED"}, headers=manager_token_headers)
    assert res3.status_code == 200
    assert res3.json()["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_14_cancel_production_plan(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 14: Cancelling plan transitions status to CANCELLED."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=2))
    }
    create_res = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    plan_id = create_res.json()["id"]

    cancel_res = await async_client.post(f"/api/v1/production-plans/{plan_id}/cancel", headers=manager_token_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_15_filtering_by_status(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 15: Filter plans by status PLANNED."""
    response = await async_client.get("/api/v1/production-plans?status=PLANNED", headers=manager_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["items"], list)


@pytest.mark.asyncio
async def test_16_filtering_by_priority(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 16: Filter plans by priority HIGH."""
    response = await async_client.get("/api/v1/production-plans?priority=HIGH", headers=manager_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["items"], list)


@pytest.mark.asyncio
async def test_17_filtering_by_product(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 17: Filter plans by product_id."""
    response = await async_client.get(f"/api/v1/production-plans?product_id={sample_product.id}", headers=manager_token_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["items"], list)


@pytest.mark.asyncio
async def test_18_pagination(
    async_client: AsyncClient,
    manager_token_headers: dict
):
    """Scenario 18: Pagination parameters limit results."""
    response = await async_client.get("/api/v1/production-plans?page=1&limit=5", headers=manager_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 5


@pytest.mark.asyncio
async def test_19_audit_log_creation(
    async_client: AsyncClient,
    manager_token_headers: dict,
    sample_product: Product,
    db_session: AsyncSession
):
    """Scenario 19: Creating plan generates AuditLog record in DB."""
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 300,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=5))
    }
    create_res = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    plan_id = create_res.json()["id"]

    stmt = select(AuditLog).where(AuditLog.entity_id == str(plan_id))
    res = await db_session.execute(stmt)
    logs = res.scalars().all()
    assert len(logs) > 0
    assert logs[0].action == "PRODUCTION_PLAN_CREATED"


@pytest.mark.asyncio
async def test_20_role_based_access_behavior(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict,
    sample_product: Product
):
    """Scenario 20: Operators can view plans but cannot create or cancel."""
    # 1. Operator can list plans (Read-only)
    list_res = await async_client.get("/api/v1/production-plans", headers=operator_token_headers)
    assert list_res.status_code == 200

    # 2. Manager creates plan
    payload = {
        "product_id": str(sample_product.id),
        "planned_quantity": 100,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=5))
    }
    create_res = await async_client.post("/api/v1/production-plans", json=payload, headers=manager_token_headers)
    plan_id = create_res.json()["id"]

    # 3. Operator attempting to cancel returns 403 Forbidden
    cancel_res = await async_client.post(f"/api/v1/production-plans/{plan_id}/cancel", headers=operator_token_headers)
    assert cancel_res.status_code == 403
