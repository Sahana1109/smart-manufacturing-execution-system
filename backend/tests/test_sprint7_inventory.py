import uuid
from datetime import date, timedelta
import pytest
from httpx import AsyncClient

from app.modules.products.models import Product
from app.modules.production_planning.models import ProductionPlan


@pytest.mark.asyncio
async def test_01_material_crud(
    async_client: AsyncClient,
    inventory_manager_token_headers: dict,
):
    """Scenario 1: Material creation, duplicate code validation, update, and deactivation."""
    # 1. Create Material
    res_create = await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-RAW-STEEL-01",
            "name": "High Carbon Steel Bar 20mm",
            "description": "Cold-drawn alloy steel rod",
            "unit": "KG",
            "reorder_level": 50,
            "initial_quantity": 200,
            "location": "BAY-A1"
        },
        headers=inventory_manager_token_headers
    )
    assert res_create.status_code == 201
    mat_data = res_create.json()
    mat_id = mat_data["id"]
    assert mat_data["material_code"] == "MAT-RAW-STEEL-01"
    assert mat_data["stock"]["quantity"] == 200
    assert mat_data["stock"]["available_quantity"] == 200

    # 2. Duplicate Code Rejection
    res_dup = await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-RAW-STEEL-01",
            "name": "Duplicate Material",
            "unit": "KG"
        },
        headers=inventory_manager_token_headers
    )
    assert res_dup.status_code == 409

    # 3. Update Material
    res_patch = await async_client.patch(
        f"/api/v1/inventory/materials/{mat_id}",
        json={"name": "High Carbon Steel Bar 20mm (Grade A)", "reorder_level": 75},
        headers=inventory_manager_token_headers
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["name"] == "High Carbon Steel Bar 20mm (Grade A)"
    assert res_patch.json()["reorder_level"] == 75

    # 4. Deactivate Material
    res_del = await async_client.delete(
        f"/api/v1/inventory/materials/{mat_id}",
        headers=inventory_manager_token_headers
    )
    assert res_del.status_code == 200
    get_mat = await async_client.get(f"/api/v1/inventory/materials/{mat_id}", headers=inventory_manager_token_headers)
    assert get_mat.json()["is_active"] is False


@pytest.mark.asyncio
async def test_02_stock_operations(
    async_client: AsyncClient,
    inventory_manager_token_headers: dict,
):
    """Scenario 2: Receive, reserve, release, consume, adjust stock and verify available quantity math."""
    # Create test material
    mat_res = await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-ALUM-SHEET-02",
            "name": "Aluminum Sheet 2mm",
            "unit": "PCS",
            "reorder_level": 20,
            "initial_quantity": 100
        },
        headers=inventory_manager_token_headers
    )
    mat_id = mat_res.json()["id"]

    # 1. Receive Stock (+50)
    rec_res = await async_client.post(
        "/api/v1/inventory/stock/receipt",
        json={"material_id": mat_id, "quantity": 50, "reference": "PO-10042 Supplier Delivery"},
        headers=inventory_manager_token_headers
    )
    assert rec_res.status_code == 200
    assert rec_res.json()["quantity"] == 150
    assert rec_res.json()["available_quantity"] == 150

    # 2. Reserve Stock (30)
    res_reserve = await async_client.post(
        "/api/v1/inventory/stock/reserve",
        json={"material_id": mat_id, "quantity": 30, "reference": "Allocation for Production"},
        headers=inventory_manager_token_headers
    )
    assert res_reserve.status_code == 200
    assert res_reserve.json()["quantity"] == 150
    assert res_reserve.json()["reserved_quantity"] == 30
    assert res_reserve.json()["available_quantity"] == 120

    # 3. Release Stock (10)
    res_rel = await async_client.post(
        "/api/v1/inventory/stock/release",
        json={"material_id": mat_id, "quantity": 10, "reference": "Release unused allocation"},
        headers=inventory_manager_token_headers
    )
    assert res_rel.status_code == 200
    assert res_rel.json()["reserved_quantity"] == 20
    assert res_rel.json()["available_quantity"] == 130

    # 4. Consume Stock (20)
    res_con = await async_client.post(
        "/api/v1/inventory/stock/consume",
        json={"material_id": mat_id, "quantity": 20, "reference": "Work order material usage"},
        headers=inventory_manager_token_headers
    )
    assert res_con.status_code == 200
    assert res_con.json()["quantity"] == 130  # 150 - 20 = 130
    assert res_con.json()["reserved_quantity"] == 0  # 20 - 20 = 0

    # 5. Adjust Stock (to 300)
    res_adj = await async_client.post(
        "/api/v1/inventory/stock/adjust",
        json={"material_id": mat_id, "new_quantity": 300, "reference": "Annual physical stock audit count"},
        headers=inventory_manager_token_headers
    )
    assert res_adj.status_code == 200
    assert res_adj.json()["quantity"] == 300
    assert res_adj.json()["available_quantity"] == 300


@pytest.mark.asyncio
async def test_03_stock_validation_rules(
    async_client: AsyncClient,
    inventory_manager_token_headers: dict,
):
    """Scenario 3: Validate negative quantity, insufficient available stock, excessive release, inactive material."""
    mat_res = await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-VAL-TEST-03",
            "name": "Validation Test Fasteners",
            "unit": "PCS",
            "reorder_level": 10,
            "initial_quantity": 50
        },
        headers=inventory_manager_token_headers
    )
    mat_id = mat_res.json()["id"]

    # 1. Reserve more than available stock (60 > 50) -> HTTP 400
    res_over = await async_client.post(
        "/api/v1/inventory/stock/reserve",
        json={"material_id": mat_id, "quantity": 60},
        headers=inventory_manager_token_headers
    )
    assert res_over.status_code == 400
    err_msg = res_over.json().get("detail") or res_over.json().get("error", {}).get("message", "")
    assert "Insufficient available stock" in err_msg

    # 2. Excessive release -> HTTP 400
    res_rel_ex = await async_client.post(
        "/api/v1/inventory/stock/release",
        json={"material_id": mat_id, "quantity": 10},  # 0 reserved currently
        headers=inventory_manager_token_headers
    )
    assert res_rel_ex.status_code == 400
    err_rel = res_rel_ex.json().get("detail") or res_rel_ex.json().get("error", {}).get("message", "")
    assert "exceeds currently reserved quantity" in err_rel

    # 3. Operations on inactive material -> HTTP 400
    await async_client.delete(f"/api/v1/inventory/materials/{mat_id}", headers=inventory_manager_token_headers)
    res_inact = await async_client.post(
        "/api/v1/inventory/stock/receipt",
        json={"material_id": mat_id, "quantity": 20},
        headers=inventory_manager_token_headers
    )
    assert res_inact.status_code == 400


@pytest.mark.asyncio
async def test_04_work_order_inventory_integration(
    async_client: AsyncClient,
    manager_token_headers: dict,
    inventory_manager_token_headers: dict,
    sample_plan: ProductionPlan,
    sample_product: Product,
):
    """Scenario 4: Work order material reservation, consumption, and invalid work order handling."""
    # 1. Create Work Order
    wo_res = await async_client.post(
        "/api/v1/work-orders",
        json={
            "production_plan_id": str(sample_plan.id),
            "product_id": str(sample_product.id),
            "planned_quantity": 25,
            "start_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=5))
        },
        headers=manager_token_headers
    )
    wo_id = wo_res.json()["id"]

    # 2. Create Material
    mat_res = await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-WO-ALL-04",
            "name": "Alloy Casting Block",
            "unit": "PCS",
            "reorder_level": 5,
            "initial_quantity": 40
        },
        headers=inventory_manager_token_headers
    )
    mat_id = mat_res.json()["id"]

    # 3. Reserve stock linked to Work Order
    res_reserve = await async_client.post(
        "/api/v1/inventory/stock/reserve",
        json={
            "material_id": mat_id,
            "work_order_id": wo_id,
            "quantity": 25,
            "reference": f"Work Order {wo_id} reservation"
        },
        headers=manager_token_headers
    )
    assert res_reserve.status_code == 200
    assert res_reserve.json()["reserved_quantity"] == 25

    # 4. Consume stock linked to Work Order
    res_con = await async_client.post(
        "/api/v1/inventory/stock/consume",
        json={
            "material_id": mat_id,
            "work_order_id": wo_id,
            "quantity": 25,
            "reference": f"Work Order {wo_id} consumption"
        },
        headers=manager_token_headers
    )
    assert res_con.status_code == 200
    assert res_con.json()["quantity"] == 15

    # 5. Invalid Work Order ID returns 404
    bad_wo_res = await async_client.post(
        "/api/v1/inventory/stock/reserve",
        json={
            "material_id": mat_id,
            "work_order_id": str(uuid.uuid4()),
            "quantity": 5
        },
        headers=manager_token_headers
    )
    assert bad_wo_res.status_code == 404


@pytest.mark.asyncio
async def test_05_stock_movements_history(
    async_client: AsyncClient,
    inventory_manager_token_headers: dict,
):
    """Scenario 5: Audit movement records generated for stock transactions."""
    mat_res = await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-MOV-HIST-05",
            "name": "Copper Wire Spool",
            "unit": "M",
            "reorder_level": 100,
            "initial_quantity": 500
        },
        headers=inventory_manager_token_headers
    )
    mat_id = mat_res.json()["id"]

    await async_client.post(
        "/api/v1/inventory/stock/reserve",
        json={"material_id": mat_id, "quantity": 100},
        headers=inventory_manager_token_headers
    )

    mov_res = await async_client.get(
        f"/api/v1/inventory/movements/{mat_id}",
        headers=inventory_manager_token_headers
    )
    assert mov_res.status_code == 200
    movements = mov_res.json()
    assert len(movements) >= 2
    types = [m["movement_type"] for m in movements]
    assert "RECEIPT" in types
    assert "RESERVATION" in types


@pytest.mark.asyncio
async def test_06_low_stock_detection(
    async_client: AsyncClient,
    inventory_manager_token_headers: dict,
):
    """Scenario 6: Low stock detection returns materials where available <= reorder_level."""
    # 1. Normal Stock Material
    await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-NORMAL-06",
            "name": "Plenty In Stock",
            "unit": "PCS",
            "reorder_level": 10,
            "initial_quantity": 100
        },
        headers=inventory_manager_token_headers
    )

    # 2. Low Stock Material
    await async_client.post(
        "/api/v1/inventory/materials",
        json={
            "material_code": "MAT-LOW-06",
            "name": "Critical Low Stock Item",
            "unit": "PCS",
            "reorder_level": 50,
            "initial_quantity": 20
        },
        headers=inventory_manager_token_headers
    )

    low_res = await async_client.get("/api/v1/inventory/low-stock", headers=inventory_manager_token_headers)
    assert low_res.status_code == 200
    low_mats = low_res.json()
    codes = [m["material_code"] for m in low_mats]
    assert "MAT-LOW-06" in codes
    assert "MAT-NORMAL-06" not in codes


@pytest.mark.asyncio
async def test_07_rbac_enforcement(
    async_client: AsyncClient,
    inventory_manager_token_headers: dict,
    operator_token_headers: dict,
    supervisor_token_headers: dict,
):
    """Scenario 7: RBAC enforcement for inventory operations."""
    # 1. Operator attempts material creation (blocked HTTP 403)
    op_create = await async_client.post(
        "/api/v1/inventory/materials",
        json={"material_code": "MAT-OP-BLOCKED", "name": "Blocked Item"},
        headers=operator_token_headers
    )
    assert op_create.status_code == 403

    # 2. Operator read access allowed (HTTP 200)
    op_read = await async_client.get("/api/v1/inventory/materials", headers=operator_token_headers)
    assert op_read.status_code == 200

    # 3. Inventory Manager full access allowed (HTTP 201)
    inv_create = await async_client.post(
        "/api/v1/inventory/materials",
        json={"material_code": "MAT-INV-OK", "name": "Allowed Item"},
        headers=inventory_manager_token_headers
    )
    assert inv_create.status_code == 201
