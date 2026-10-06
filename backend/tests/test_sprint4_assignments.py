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
from app.modules.work_orders.models import WorkOrder
from app.modules.audit_logs.models import AuditLog


@pytest.mark.asyncio
async def test_01_create_machine_successfully(
    async_client: AsyncClient,
    manager_token_headers: dict
):
    """Scenario 1: Production Manager creates a valid machine entity."""
    payload = {
        "machine_code": "MAC-TEST-001",
        "name": "Haas CNC Milling Center 5-Axis",
        "status": "OPERATIONAL",
        "is_active": True
    }
    response = await async_client.post("/api/v1/machines", json=payload, headers=manager_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["machine_code"] == "MAC-TEST-001"
    assert data["status"] == "OPERATIONAL"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_02_get_and_list_machines(
    async_client: AsyncClient,
    operator_token_headers: dict,
    manager_token_headers: dict
):
    """Scenario 2: Authenticated user retrieves machines list and details."""
    # Ensure at least one machine is created
    payload = {
        "machine_code": "MAC-LIST-001",
        "name": "Listing Machine Test"
    }
    await async_client.post("/api/v1/machines", json=payload, headers=manager_token_headers)

    res = await async_client.get("/api/v1/machines", headers=operator_token_headers)
    assert res.status_code == 200
    machines = res.json()
    assert isinstance(machines, list)
    assert len(machines) > 0

    machine_id = machines[0]["id"]
    detail_res = await async_client.get(f"/api/v1/machines/{machine_id}", headers=operator_token_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == machine_id


@pytest.mark.asyncio
async def test_03_update_machine_details(
    async_client: AsyncClient,
    manager_token_headers: dict
):
    """Scenario 3: Production Manager updates machine name and code."""
    # Create test machine first
    payload = {
        "machine_code": "MAC-UPDATE-01",
        "name": "Old Machine Name"
    }
    create_res = await async_client.post("/api/v1/machines", json=payload, headers=manager_token_headers)
    m_id = create_res.json()["id"]

    update_payload = {
        "name": "Updated Machine Name Pro"
    }
    update_res = await async_client.put(f"/api/v1/machines/{m_id}", json=update_payload, headers=manager_token_headers)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Updated Machine Name Pro"


@pytest.mark.asyncio
async def test_04_change_machine_status(
    async_client: AsyncClient,
    supervisor_token_headers: dict
):
    """Scenario 4: Supervisor changes machine status (e.g. to MAINTENANCE)."""
    payload = {
        "machine_code": "MAC-STATUS-01",
        "name": "Lathe Machine 200"
    }
    c_res = await async_client.post("/api/v1/machines", json=payload, headers=supervisor_token_headers)
    m_id = c_res.json()["id"]

    patch_res = await async_client.patch(
        f"/api/v1/machines/{m_id}/status",
        json={"status": "MAINTENANCE"},
        headers=supervisor_token_headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "MAINTENANCE"


@pytest.mark.asyncio
async def test_05_valid_machine_assignment(
    async_client: AsyncClient,
    supervisor_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    sample_machine: Machine
):
    """Scenario 5: Supervisor assigns an operational machine to a work order."""
    wo_payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 100,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    wo_res = await async_client.post("/api/v1/work-orders", json=wo_payload, headers=manager_token_headers)
    wo_id = wo_res.json()["id"]

    assign_res = await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"assigned_machine_id": str(sample_machine.id)},
        headers=supervisor_token_headers
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_machine_id"] == str(sample_machine.id)


@pytest.mark.asyncio
async def test_06_invalid_machine_assignment_nonexistent(
    async_client: AsyncClient,
    supervisor_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 6: Assigning a non-existent machine ID returns 400 Bad Request."""
    wo_payload = {
        "production_plan_id": str(sample_plan.id),
        "product_id": str(sample_product.id),
        "planned_quantity": 50,
        "start_date": str(date.today()),
        "due_date": str(date.today() + timedelta(days=3))
    }
    wo_res = await async_client.post("/api/v1/work-orders", json=wo_payload, headers=manager_token_headers)
    wo_id = wo_res.json()["id"]

    assign_res = await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"assigned_machine_id": str(uuid.uuid4())},
        headers=supervisor_token_headers
    )
    assert assign_res.status_code == 400


@pytest.mark.asyncio
async def test_07_assignment_to_nonexistent_work_order(
    async_client: AsyncClient,
    supervisor_token_headers: dict,
    sample_machine: Machine
):
    """Scenario 7: Assigning resources to a non-existent work order returns 404 Not Found."""
    fake_wo_id = uuid.uuid4()
    assign_res = await async_client.patch(
        f"/api/v1/work-orders/{fake_wo_id}/assign",
        json={"assigned_machine_id": str(sample_machine.id)},
        headers=supervisor_token_headers
    )
    assert assign_res.status_code == 404


@pytest.mark.asyncio
async def test_08_assignment_of_machine_in_maintenance_fails(
    async_client: AsyncClient,
    supervisor_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 8: Assigning a machine in MAINTENANCE status returns 400 Bad Request."""
    # Create machine in maintenance status
    m_res = await async_client.post(
        "/api/v1/machines",
        json={"machine_code": "MAC-MAINT-99", "name": "Broken Mill", "status": "MAINTENANCE"},
        headers=manager_token_headers
    )
    m_id = m_res.json()["id"]

    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 40,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=2))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    assign_res = await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"assigned_machine_id": m_id},
        headers=supervisor_token_headers
    )
    assert assign_res.status_code == 400
    res_data = assign_res.json()
    err_msg = str(res_data.get("detail") or res_data.get("error", {}).get("message", ""))
    assert "MAINTENANCE" in err_msg


@pytest.mark.asyncio
async def test_09_valid_employee_assignment(
    async_client: AsyncClient,
    supervisor_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    sample_employee: Employee
):
    """Scenario 9: Supervisor assigns active employee operator to work order."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 60,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    assign_res = await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"assigned_employee_id": str(sample_employee.id)},
        headers=supervisor_token_headers
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_employee_id"] == str(sample_employee.id)


@pytest.mark.asyncio
async def test_10_invalid_employee_assignment_nonexistent(
    async_client: AsyncClient,
    supervisor_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 10: Assigning a non-existent employee ID returns 400 Bad Request."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 60,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    assign_res = await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"assigned_employee_id": str(uuid.uuid4())},
        headers=supervisor_token_headers
    )
    assert assign_res.status_code == 400


@pytest.mark.asyncio
async def test_11_unassign_machine_and_employee(
    async_client: AsyncClient,
    supervisor_token_headers: dict,
    manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
    sample_machine: Machine,
    sample_employee: Employee
):
    """Scenario 11: Unassigning machine and employee resources from work order."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 75,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=4))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    # Assign both
    await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"assigned_machine_id": str(sample_machine.id), "assigned_employee_id": str(sample_employee.id)},
        headers=supervisor_token_headers
    )

    # Unassign machine
    unassign_m = await async_client.delete(f"/api/v1/work-orders/{wo_id}/assign/machine", headers=supervisor_token_headers)
    assert unassign_m.status_code == 200
    assert unassign_m.json()["assigned_machine_id"] is None

    # Unassign employee
    unassign_e = await async_client.delete(f"/api/v1/work-orders/{wo_id}/assign/employee", headers=supervisor_token_headers)
    assert unassign_e.status_code == 200
    assert unassign_e.json()["assigned_employee_id"] is None


@pytest.mark.asyncio
async def test_12_unauthorized_machine_management(
    async_client: AsyncClient,
    operator_token_headers: dict
):
    """Scenario 12: Operator attempting to create machine receives 403 Forbidden."""
    payload = {
        "machine_code": "MAC-UNAUTH-01",
        "name": "Unauthorized Machine"
    }
    res = await async_client.post("/api/v1/machines", json=payload, headers=operator_token_headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_13_employee_crud_and_rbac(
    async_client: AsyncClient,
    manager_token_headers: dict,
    operator_token_headers: dict
):
    """Scenario 13: Full Employee CRUD and RBAC enforcement."""
    # 1. Operator creation fails (403)
    emp_payload = {
        "employee_code": "EMP-TEST-99",
        "first_name": "Test",
        "last_name": "Operator",
        "role_title": "CNC Tech"
    }
    r_forbidden = await async_client.post("/api/v1/employees", json=emp_payload, headers=operator_token_headers)
    assert r_forbidden.status_code == 403

    # 2. Manager creation succeeds (201)
    r_create = await async_client.post("/api/v1/employees", json=emp_payload, headers=manager_token_headers)
    assert r_create.status_code == 201
    emp_id = r_create.json()["id"]

    # 3. Manager update succeeds (200)
    r_update = await async_client.put(
        f"/api/v1/employees/{emp_id}",
        json={"role_title": "Senior CNC Specialist"},
        headers=manager_token_headers
    )
    assert r_update.status_code == 200
    assert r_update.json()["role_title"] == "Senior CNC Specialist"

    # 4. Deactivate employee (200)
    r_del = await async_client.delete(f"/api/v1/employees/{emp_id}", headers=manager_token_headers)
    assert r_del.status_code == 200
    assert r_del.json()["is_active"] is False


@pytest.mark.asyncio
async def test_14_machine_status_autosync_during_work_order_execution(
    async_client: AsyncClient,
    manager_token_headers: dict,
    supervisor_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product
):
    """Scenario 14: Machine status updates to IN_USE when work order transitions to IN_PROGRESS."""
    # Create operational machine
    m_res = await async_client.post(
        "/api/v1/machines",
        json={"machine_code": "MAC-EXEC-01", "name": "Milling Cell", "status": "OPERATIONAL"},
        headers=manager_token_headers
    )
    m_id = m_res.json()["id"]

    # Create work order
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

    # Assign machine
    await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/assign",
        json={"assigned_machine_id": m_id},
        headers=supervisor_token_headers
    )

    # Transition WO to RELEASED then IN_PROGRESS
    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "RELEASED"}, headers=manager_token_headers)
    await async_client.patch(f"/api/v1/work-orders/{wo_id}/status", json={"status": "IN_PROGRESS"}, headers=manager_token_headers)

    # Check machine status is now IN_USE
    m_detail = await async_client.get(f"/api/v1/machines/{m_id}", headers=manager_token_headers)
    assert m_detail.json()["status"] == "IN_USE"
