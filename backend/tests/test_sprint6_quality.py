import uuid
from datetime import date, timedelta
import pytest
from httpx import AsyncClient

from app.modules.products.models import Product
from app.modules.production_planning.models import ProductionPlan
from app.modules.machines.models import Machine


async def _create_completed_work_order(async_client: AsyncClient, headers: dict, plan: ProductionPlan, product: Product) -> str:
    """Helper creating and completing a work order for quality testing."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(plan.id),
            "product_id": str(product.id),
            "planned_quantity": 100,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=3))
        },
        headers=headers
    )
    wo_id = wo_res.json()["id"]

    # Release work order
    await async_client.patch(
        f"/api/v1/work-orders/{wo_id}/status",
        json={"status": "RELEASED"},
        headers=headers
    )

    # Start production execution
    await async_client.post(f"/api/v1/work-orders/{wo_id}/start", headers=headers)

    # Complete production execution
    await async_client.post(
        f"/api/v1/work-orders/{wo_id}/complete",
        json={"produced_quantity": 100, "notes": "Production complete"},
        headers=headers
    )

    return wo_id


@pytest.mark.asyncio
async def test_01_create_inspection_successful(
    async_client: AsyncClient,
    manager_token_headers: dict,
    inspector_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
):
    """Scenario 1: Create a valid quality inspection for a COMPLETED work order."""
    wo_id = await _create_completed_work_order(async_client, manager_token_headers, sample_plan, sample_product)

    res = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": 100,
            "accepted_quantity": 95,
            "rejected_quantity": 5,
            "status": "PASSED",
            "remarks": "Batch passed QA standards with minor acceptable scrap"
        },
        headers=inspector_token_headers
    )
    assert res.status_code == 201
    data = res.json()
    assert data["work_order_id"] == wo_id
    assert data["status"] == "PASSED"
    assert data["inspected_quantity"] == 100
    assert data["accepted_quantity"] == 95
    assert data["rejected_quantity"] == 5

    # Verify Work Order quality_status property dynamically resolves to PASSED
    wo_get = await async_client.get(f"/api/v1/work-orders/{wo_id}", headers=manager_token_headers)
    assert wo_get.json()["quality_status"] == "PASSED"


@pytest.mark.asyncio
async def test_02_create_inspection_requires_completed_work_order(
    async_client: AsyncClient,
    manager_token_headers: dict,
    inspector_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
):
    """Scenario 2: Creating inspection for non-completed work order fails with 400."""
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 50,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=2))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    res = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": 50,
            "accepted_quantity": 50,
            "rejected_quantity": 0,
            "status": "PASSED"
        },
        headers=inspector_token_headers
    )
    assert res.status_code == 400
    err_msg = res.json().get("detail") or res.json().get("error", {}).get("message", "")
    assert "Only completed work orders" in err_msg


@pytest.mark.asyncio
async def test_03_inspection_quantity_validations(
    async_client: AsyncClient,
    manager_token_headers: dict,
    inspector_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
):
    """Scenario 3: Validate quantity constraints (negative values and sum exceeding inspected)."""
    wo_id = await _create_completed_work_order(async_client, manager_token_headers, sample_plan, sample_product)

    # 1. Negative quantity
    res_neg = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": -10,
            "accepted_quantity": 0,
            "rejected_quantity": 0,
            "status": "FAILED"
        },
        headers=inspector_token_headers
    )
    assert res_neg.status_code == 422 or res_neg.status_code == 400

    # 2. Accepted + Rejected > Inspected
    res_exceed = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": 100,
            "accepted_quantity": 80,
            "rejected_quantity": 30,  # 80+30=110 > 100
            "status": "FAILED"
        },
        headers=inspector_token_headers
    )
    assert res_exceed.status_code == 400
    err_exceed_msg = res_exceed.json().get("detail") or res_exceed.json().get("error", {}).get("message", "")
    assert "cannot exceed inspected quantity" in err_exceed_msg


@pytest.mark.asyncio
async def test_04_update_inspection_and_statuses(
    async_client: AsyncClient,
    manager_token_headers: dict,
    inspector_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
):
    """Scenario 4: Update an inspection status (REWORK_REQUIRED -> PASSED)."""
    wo_id = await _create_completed_work_order(async_client, manager_token_headers, sample_plan, sample_product)

    # Create inspection with REWORK_REQUIRED
    create_res = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": 100,
            "accepted_quantity": 70,
            "rejected_quantity": 30,
            "status": "REWORK_REQUIRED",
            "remarks": "Requires burr removal on edge"
        },
        headers=inspector_token_headers
    )
    insp_id = create_res.json()["id"]

    # Update inspection to PASSED after rework
    patch_res = await async_client.patch(
        f"/api/v1/quality/inspections/{insp_id}",
        json={
            "accepted_quantity": 95,
            "rejected_quantity": 5,
            "status": "PASSED",
            "remarks": "Rework completed successfully"
        },
        headers=inspector_token_headers
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["status"] == "PASSED"
    assert data["accepted_quantity"] == 95
    assert data["rejected_quantity"] == 5


@pytest.mark.asyncio
async def test_05_defect_crud_operations(
    async_client: AsyncClient,
    manager_token_headers: dict,
    inspector_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
):
    """Scenario 5: Defect CRUD operations under a quality inspection."""
    wo_id = await _create_completed_work_order(async_client, manager_token_headers, sample_plan, sample_product)

    insp_res = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": 100,
            "accepted_quantity": 90,
            "rejected_quantity": 10,
            "status": "FAILED"
        },
        headers=inspector_token_headers
    )
    insp_id = insp_res.json()["id"]

    # 1. Create Defect
    defect_res = await async_client.post(
        f"/api/v1/quality/inspections/{insp_id}/defects",
        json={
            "defect_type": "SURFACE",
            "severity": "HIGH",
            "description": "Scratches on outer surface",
            "quantity": 10,
            "remarks": "Tooling misalignment"
        },
        headers=inspector_token_headers
    )
    assert defect_res.status_code == 201
    defect_data = defect_res.json()
    defect_id = defect_data["id"]
    assert defect_data["defect_type"] == "SURFACE"
    assert defect_data["quantity"] == 10

    # 2. List Defects
    list_res = await async_client.get(f"/api/v1/quality/inspections/{insp_id}/defects", headers=inspector_token_headers)
    assert list_res.status_code == 200
    defects = list_res.json()
    assert len(defects) == 1

    # 3. Update Defect
    patch_defect = await async_client.patch(
        f"/api/v1/quality/defects/{defect_id}",
        json={"severity": "CRITICAL", "remarks": "Updated severity to CRITICAL"},
        headers=inspector_token_headers
    )
    assert patch_defect.status_code == 200
    assert patch_defect.json()["severity"] == "CRITICAL"

    # 4. Delete Defect
    del_res = await async_client.delete(f"/api/v1/quality/defects/{defect_id}", headers=inspector_token_headers)
    assert del_res.status_code == 200

    # Confirm list is now empty
    list_after = await async_client.get(f"/api/v1/quality/inspections/{insp_id}/defects", headers=inspector_token_headers)
    assert len(list_after.json()) == 0


@pytest.mark.asyncio
async def test_06_quality_summary(
    async_client: AsyncClient,
    manager_token_headers: dict,
    inspector_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
):
    """Scenario 6: Quality summary metrics calculation."""
    wo_id = await _create_completed_work_order(async_client, manager_token_headers, sample_plan, sample_product)

    insp_res = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": 100,
            "accepted_quantity": 80,
            "rejected_quantity": 20,
            "status": "FAILED"
        },
        headers=inspector_token_headers
    )
    insp_id = insp_res.json()["id"]

    await async_client.post(
        f"/api/v1/quality/inspections/{insp_id}/defects",
        json={"defect_type": "DIMENSIONAL", "severity": "HIGH", "quantity": 15},
        headers=inspector_token_headers
    )

    summary_res = await async_client.get("/api/v1/quality/summary", headers=inspector_token_headers)
    assert summary_res.status_code == 200
    s_data = summary_res.json()
    assert s_data["total_inspections"] >= 1
    assert s_data["failed"] >= 1
    assert s_data["total_rejected_quantity"] >= 20
    assert s_data["total_defects"] >= 15


@pytest.mark.asyncio
async def test_07_rbac_enforcement(
    async_client: AsyncClient,
    manager_token_headers: dict,
    operator_token_headers: dict,
    inspector_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
):
    """Scenario 7: Operator read-only access vs Quality Inspector write permissions."""
    wo_id = await _create_completed_work_order(async_client, manager_token_headers, sample_plan, sample_product)

    # 1. Operator write blocked (HTTP 403)
    op_create = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": 50,
            "accepted_quantity": 50,
            "rejected_quantity": 0,
            "status": "PASSED"
        },
        headers=operator_token_headers
    )
    assert op_create.status_code == 403

    # 2. Inspector write allowed (HTTP 201)
    insp_create = await async_client.post(
        "/api/v1/quality/inspections",
        json={
            "work_order_id": wo_id,
            "inspected_quantity": 50,
            "accepted_quantity": 50,
            "rejected_quantity": 0,
            "status": "PASSED"
        },
        headers=inspector_token_headers
    )
    assert insp_create.status_code == 201

    # 3. Operator read allowed (HTTP 200)
    op_read = await async_client.get("/api/v1/quality/inspections", headers=operator_token_headers)
    assert op_read.status_code == 200


@pytest.mark.asyncio
async def test_08_invalid_ids_handling(
    async_client: AsyncClient,
    inspector_token_headers: dict,
):
    """Scenario 8: Non-existent inspection or defect IDs return HTTP 404."""
    random_id = str(uuid.uuid4())

    get_insp = await async_client.get(f"/api/v1/quality/inspections/{random_id}", headers=inspector_token_headers)
    assert get_insp.status_code == 404

    patch_defect = await async_client.patch(
        f"/api/v1/quality/defects/{random_id}",
        json={"remarks": "Invalid test"},
        headers=inspector_token_headers
    )
    assert patch_defect.status_code == 404

    del_defect = await async_client.delete(f"/api/v1/quality/defects/{random_id}", headers=inspector_token_headers)
    assert del_defect.status_code == 404
