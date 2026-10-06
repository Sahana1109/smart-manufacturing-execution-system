import uuid
from datetime import date, datetime, timedelta, timezone
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_complete_end_to_end_mes_workflow(
    async_client: AsyncClient,
    admin_token_headers: dict,
    manager_token_headers: dict,
    supervisor_token_headers: dict,
    operator_token_headers: dict,
    inspector_token_headers: dict,
    inventory_manager_token_headers: dict,
):
    """
    End-to-End System Acceptance Test covering Sprints 1 through 8:
    Admin Login -> Material & Stock Creation -> Machine & Operator Creation ->
    Production Plan -> Work Order Creation -> Machine & Operator Assignment ->
    Work Order Release & Start -> Downtime Recording -> Production Completion ->
    Quality Inspection & Defect Recording -> Material Reservation & Consumption ->
    Management Dashboard KPI Verification.
    """
    # 1. Create Material & Stock (Sprint 7)
    res_mat = await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-E2E-STEEL-01",
            "name": "E2E Hardened Alloy Steel Rod",
            "unit": "PCS",
            "reorder_level": 50,
            "initial_quantity": 500,
            "location": "MAIN-BAY-E2E",
        },
        headers=inventory_manager_token_headers,
    )
    assert res_mat.status_code == 201
    mat_id = res_mat.json()["id"]

    # 2. Create Machine & Operator (Sprint 4)
    res_mac = await async_client.post(
        "/api/v1/machines",
        json={
            "machine_code": "CNC-E2E-MILL-01",
            "name": "High Precision 5-Axis CNC Mill",
            "status": "OPERATIONAL",
        },
        headers=admin_token_headers,
    )
    assert res_mac.status_code == 201
    mac_id = res_mac.json()["id"]

    res_emp = await async_client.post(
        "/api/v1/employees",
        json={
            "employee_code": "EMP-E2E-OP-01",
            "first_name": "Robert",
            "last_name": "Taylor",
            "role_title": "Lead CNC Operator",
        },
        headers=admin_token_headers,
    )
    assert res_emp.status_code == 201
    emp_id = res_emp.json()["id"]

    # 3. Create Product & Production Plan (Sprint 2)
    res_prod = await async_client.post(
        "/api/v1/products",
        json={
            "product_code": "PROD-E2E-GEAR-01",
            "name": "Transmission Precision Pinion Gear",
            "unit_of_measure": "PCS",
        },
        headers=admin_token_headers,
    )
    assert res_prod.status_code == 201
    prod_id = res_prod.json()["id"]

    res_plan = await async_client.post(
        "/api/v1/production-plans",
        json={
            "product_id": prod_id,
            "planned_quantity": 100,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=7)),
            "priority": "HIGH",
            "notes": "E2E Integration Validation Batch",
        },
        headers=manager_token_headers,
    )
    assert res_plan.status_code == 201
    plan_id = res_plan.json()["id"]

    # 4. Create Work Order (Sprint 3)
    res_wo = await async_client.post(
        "/api/v1/work-orders",
        json={
            "work_order_number": "WO-E2E-2026-001",
            "production_plan_id": plan_id,
            "product_id": prod_id,
            "planned_quantity": 100,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3)),
            "priority": "HIGH",
        },
        headers=manager_token_headers,
    )
    assert res_wo.status_code == 201
    wo_id = res_wo.json()["id"]

    # 5. Assign Machine & Operator (Sprint 4)
    res_assign = await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"assigned_machine_id": mac_id, "assigned_employee_id": emp_id},
        headers=supervisor_token_headers,
    )
    assert res_assign.status_code == 200
    assert res_assign.json()["assigned_machine_id"] == mac_id

    # 6. Release & Start Production Execution (Sprint 5)
    await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/status",
        json={"status": "RELEASED"},
        headers=manager_token_headers,
    )

    res_start = await async_client.post(
        f"/api/v1/work-orders/{wo_id}/start",
        headers=operator_token_headers,
    )
    assert res_start.status_code == 200
    assert res_start.json()["status"] == "IN_PROGRESS"

    # Machine status auto-synchronized to IN_USE
    res_mac_check = await async_client.get(f"/api/v1/machines/{mac_id}", headers=operator_token_headers)
    assert res_mac_check.json()["status"] == "IN_USE"

    # 7. Record Downtime (Sprint 5)
    now_iso = datetime.now(timezone.utc).isoformat()
    res_dt = await async_client.post(
        f"/api/v1/work-orders/{wo_id}/downtime",
        json={
            "work_order_id": wo_id,
            "machine_id": mac_id,
            "start_time": now_iso,
            "duration_minutes": 15,
            "reason": "TOOL_CALIBRATION",
            "remarks": "Standard cutter blade re-alignment",
        },
        headers=operator_token_headers,
    )
    assert res_dt.status_code == 201

    # 8. Complete Work Order Execution (Sprint 5)
    res_comp = await async_client.post(
        f"/api/v1/work-orders/{wo_id}/complete",
        json={"produced_quantity": 95, "notes": "95 units produced successfully"},
        headers=operator_token_headers,
    )
    assert res_comp.status_code == 200
    assert res_comp.json()["status"] == "COMPLETED"
    assert res_comp.json()["produced_quantity"] == 95

    # 9. Perform Quality Inspection & Log Defect (Sprint 6)
    res_insp = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": 95,
            "accepted_quantity": 90,
            "rejected_quantity": 5,
            "status": "PASSED",
            "remarks": "Batch passed QA tolerances; 5 scrap units discarded",
        },
        headers=inspector_token_headers,
    )
    assert res_insp.status_code == 201
    insp_id = res_insp.json()["id"]

    res_def = await async_client.post(
        f"/api/v1/quality/inspections/{insp_id}/defects",
        json={
            "defect_type": "SURFACE",
            "severity": "MEDIUM",
            "description": "Minor surface scratches",
            "quantity": 5,
        },
        headers=inspector_token_headers,
    )
    assert res_def.status_code == 201

    # 10. Reserve & Consume Material Stock (Sprint 7)
    res_res = await async_client.post(
        "/api/v1/inventory/stock/reserve",
        json={"material_id": mat_id, "work_order_id": wo_id, "quantity": 100},
        headers=inventory_manager_token_headers,
    )
    assert res_res.status_code == 200
    assert res_res.json()["reserved_quantity"] == 100

    res_con = await async_client.post(
        "/api/v1/inventory/stock/consume",
        json={"material_id": mat_id, "work_order_id": wo_id, "quantity": 95},
        headers=inventory_manager_token_headers,
    )
    assert res_con.status_code == 200
    assert res_con.json()["quantity"] == 405  # 500 - 95 = 405

    # 11. Verify Management Dashboard Reports (Sprint 8)
    res_dash = await async_client.get("/api/v1/reports/dashboard", headers=admin_token_headers)
    assert res_dash.status_code == 200
    d = res_dash.json()

    # Production KPIs
    assert d["production"]["total_work_orders"] == 1
    assert d["production"]["completed"] == 1
    assert d["production"]["total_produced_quantity"] == 95
    assert d["production"]["completion_percentage"] == 100.0

    # Quality KPIs
    assert d["quality"]["total_inspections"] == 1
    assert d["quality"]["passed"] == 1
    assert d["quality"]["total_inspected_quantity"] == 95
    assert d["quality"]["total_accepted_quantity"] == 90
    assert d["quality"]["total_rejected_quantity"] == 5
    assert d["quality"]["total_defects"] == 5

    # Inventory KPIs
    assert d["inventory"]["total_materials"] == 1
    assert d["inventory"]["total_quantity"] == 405

    # Machine KPIs
    assert d["machines"]["total_machines"] == 1

    # Operator KPIs
    assert d["operators"]["total_operators"] == 1
