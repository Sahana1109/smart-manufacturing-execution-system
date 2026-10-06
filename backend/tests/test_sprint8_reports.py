import uuid
from datetime import date, timedelta
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_01_reports_empty_state(
    async_client: AsyncClient,
    admin_token_headers: dict,
):
    """Verify that report endpoints return valid empty summary metrics when database has no records."""
    # 1. Dashboard summary
    res_dash = await async_client.get("/api/v1/reports/dashboard", headers=admin_token_headers)
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert dash_data["production"]["total_work_orders"] == 0
    assert dash_data["quality"]["total_inspections"] == 0
    assert dash_data["inventory"]["total_materials"] == 0
    assert dash_data["machines"]["total_machines"] == 0
    assert dash_data["operators"]["total_operators"] == 0

    # 2. Individual Report Endpoints
    res_prod = await async_client.get("/api/v1/reports/production", headers=admin_token_headers)
    assert res_prod.status_code == 200
    assert res_prod.json()["total_work_orders"] == 0

    res_qual = await async_client.get("/api/v1/reports/quality", headers=admin_token_headers)
    assert res_qual.status_code == 200
    assert res_qual.json()["total_inspections"] == 0

    res_inv = await async_client.get("/api/v1/reports/inventory", headers=admin_token_headers)
    assert res_inv.status_code == 200
    assert res_inv.json()["total_materials"] == 0

    res_mach = await async_client.get("/api/v1/reports/machines", headers=admin_token_headers)
    assert res_mach.status_code == 200
    assert res_mach.json()["total_machines"] == 0

    res_op = await async_client.get("/api/v1/reports/operators", headers=admin_token_headers)
    assert res_op.status_code == 200
    assert res_op.json()["total_operators"] == 0


@pytest.mark.asyncio
async def test_02_reports_with_data(
    async_client: AsyncClient,
    admin_token_headers: dict,
    manager_token_headers: dict,
    operator_token_headers: dict,
    inventory_manager_token_headers: dict,
):
    """Seed sample data and verify production, quality, inventory, machine, and operator KPI calculations."""
    # 1. Create Product & Plan
    res_prod = await async_client.post(
        "/api/v1/products",
        json={"product_code": "PROD-REP-01", "name": "Report Engine Block", "unit_of_measure": "PCS"},
        headers=admin_token_headers,
    )
    product_id = res_prod.json()["id"]

    res_plan = await async_client.post(
        "/api/v1/production-plans",
        json={
            "product_id": product_id,
            "planned_quantity": 500,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=5)),
            "priority": "HIGH",
        },
        headers=manager_token_headers,
    )
    assert res_plan.status_code == 201
    plan_id = res_plan.json()["id"]

    # 2. Create Work Orders
    res_wo1 = await async_client.post(
        "/api/v1/work-orders",
        json={
            "work_order_number": "WO-REP-101",
            "production_plan_id": plan_id,
            "product_id": product_id,
            "planned_quantity": 200,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=2)),
            "priority": "HIGH",
        },
        headers=manager_token_headers,
    )
    assert res_wo1.status_code == 201
    wo1_id = res_wo1.json()["id"]

    res_wo2 = await async_client.post(
        "/api/v1/work-orders",
        json={
            "work_order_number": "WO-REP-102",
            "production_plan_id": plan_id,
            "product_id": product_id,
            "planned_quantity": 300,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3)),
            "priority": "MEDIUM",
        },
        headers=manager_token_headers,
    )
    assert res_wo2.status_code == 201
    wo2_id = res_wo2.json()["id"]

    # Transition WO1 to COMPLETED with produced_quantity
    await async_client.patch(
        f"/api/v1/work-orders/{wo1_id}/status",
        json={"status": "RELEASED"},
        headers=manager_token_headers,
    )
    await async_client.post(f"/api/v1/work-orders/{wo1_id}/start", headers=operator_token_headers)
    comp_res = await async_client.post(
        f"/api/v1/work-orders/{wo1_id}/complete",
        json={"produced_quantity": 200},
        headers=operator_token_headers,
    )
    assert comp_res.status_code == 200

    # 3. Create Quality Inspection for WO1
    await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo1_id,
            "inspected_quantity": 200,
            "accepted_quantity": 180,
            "rejected_quantity": 20,
            "status": "PASSED",
            "remarks": "Batch meets high tolerance standards",
        },
        headers=admin_token_headers,
    )

    # 4. Create Material & Receive Stock
    res_mat = await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-REP-ALU-01",
            "name": "Aluminium Alloy Billet",
            "unit": "KG",
            "reorder_level": 100,
            "initial_quantity": 80,  # low stock state: 80 <= 100
        },
        headers=inventory_manager_token_headers,
    )
    mat_id = res_mat.json()["id"]

    # 5. Create Machine & Employee
    await async_client.post(
        "/api/v1/machines",
        json={"machine_code": "CNC-REP-01", "name": "5-Axis CNC Mill", "status": "OPERATIONAL"},
        headers=admin_token_headers,
    )

    await async_client.post(
        "/api/v1/employees",
        json={"employee_code": "EMP-REP-01", "first_name": "John", "last_name": "Doe", "role_title": "Operator"},
        headers=admin_token_headers,
    )

    # 6. Check Reports APIs
    # Production Report
    res_p = await async_client.get("/api/v1/reports/production", headers=admin_token_headers)
    assert res_p.status_code == 200
    p_data = res_p.json()
    assert p_data["total_work_orders"] == 2
    assert p_data["completed"] == 1
    assert p_data["pending"] == 1  # wo2 is DRAFT
    assert p_data["total_planned_quantity"] == 500
    assert p_data["total_produced_quantity"] == 200
    assert p_data["completion_percentage"] == 50.0

    # Quality Report
    res_q = await async_client.get("/api/v1/reports/quality", headers=admin_token_headers)
    assert res_q.status_code == 200
    q_data = res_q.json()
    assert q_data["total_inspections"] == 1
    assert q_data["passed"] == 1
    assert q_data["total_inspected_quantity"] == 200
    assert q_data["total_accepted_quantity"] == 180
    assert q_data["total_rejected_quantity"] == 20

    # Inventory Report
    res_i = await async_client.get("/api/v1/reports/inventory", headers=admin_token_headers)
    assert res_i.status_code == 200
    i_data = res_i.json()
    assert i_data["total_materials"] == 1
    assert i_data["low_stock_count"] == 1
    assert i_data["low_stock_materials"][0]["id"] == mat_id

    # Machine Report
    res_m = await async_client.get("/api/v1/reports/machines", headers=admin_token_headers)
    assert res_m.status_code == 200
    m_data = res_m.json()
    assert m_data["total_machines"] == 1
    assert m_data["operational"] == 1

    # Operator Report
    res_o = await async_client.get("/api/v1/reports/operators", headers=admin_token_headers)
    assert res_o.status_code == 200
    o_data = res_o.json()
    assert o_data["total_operators"] == 1
    assert o_data["active_operators"] == 1

    # Consolidated Dashboard Summary
    res_dash = await async_client.get("/api/v1/reports/dashboard", headers=admin_token_headers)
    assert res_dash.status_code == 200
    dash = res_dash.json()
    assert dash["production"]["total_work_orders"] == 2
    assert dash["quality"]["passed"] == 1
    assert dash["inventory"]["total_materials"] == 1
    assert dash["machines"]["operational"] == 1
    assert dash["operators"]["total_operators"] == 1


@pytest.mark.asyncio
async def test_03_date_filtering_validation(
    async_client: AsyncClient,
    admin_token_headers: dict,
):
    """Verify valid and invalid date range filtering behavior."""
    today_str = str(date.today())
    tomorrow_str = str(date.today() + timedelta(days=1))
    yesterday_str = str(date.today() - timedelta(days=1))

    # Valid range
    res_valid = await async_client.get(
        f"/api/v1/reports/production?from_date={yesterday_str}&to_date={tomorrow_str}",
        headers=admin_token_headers,
    )
    assert res_valid.status_code == 200

    # Invalid range (from_date > to_date)
    res_invalid = await async_client.get(
        f"/api/v1/reports/production?from_date={tomorrow_str}&to_date={yesterday_str}",
        headers=admin_token_headers,
    )
    assert res_invalid.status_code == 400
    assert "from_date cannot be after to_date" in str(res_invalid.json())


@pytest.mark.asyncio
async def test_04_rbac_report_access(
    async_client: AsyncClient,
    admin_token_headers: dict,
    manager_token_headers: dict,
    supervisor_token_headers: dict,
    inspector_token_headers: dict,
    inventory_manager_token_headers: dict,
    operator_token_headers: dict,
):
    """Verify report access across all system roles."""
    roles_tokens = [
        ("ADMIN", admin_token_headers),
        ("PRODUCTION_MANAGER", manager_token_headers),
        ("SUPERVISOR", supervisor_token_headers),
        ("QUALITY_INSPECTOR", inspector_token_headers),
        ("INVENTORY_MANAGER", inventory_manager_token_headers),
        ("OPERATOR", operator_token_headers),
    ]

    for role_name, token in roles_tokens:
        res = await async_client.get("/api/v1/reports/dashboard", headers=token)
        assert res.status_code == 200, f"Role {role_name} should have access to /api/v1/reports/dashboard"

        res_p = await async_client.get("/api/v1/reports/production", headers=token)
        assert res_p.status_code == 200, f"Role {role_name} should have access to /api/v1/reports/production"
