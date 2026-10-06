# SmartMES - Sprint 7 Documentation: Inventory & Material Tracking Module

## 🎯 Sprint Goal
Implement a complete Inventory and Material Tracking module for SmartMES. The module enables creating and managing material master entities, tracking stock levels (`quantity`, `reserved_quantity`, `available_quantity`), processing stock transactions (`RECEIPT`, `RESERVATION`, `RELEASE`, `CONSUMPTION`, `ADJUSTMENT`), linking material allocations to Work Orders during production, detecting low-stock materials, viewing real-time stock movement audit logs via a dedicated Next.js Inventory Dashboard (`/inventory`), and enforcing strict RBAC permissions.

---

## 📋 User Stories & Acceptance Criteria

### US-INV-001: Material Catalog Management
- **User Story**: As an Inventory Manager or Admin, I want to create and manage raw materials, components, and consumables so that shop floor material requirements are tracked.
- **Acceptance Criteria**:
  - `POST /api/v1/inventory/materials` creates a material entity with code, name, description, unit (`PCS`, `KG`, `L`, `M`, `OTHER`), reorder level, and optional initial stock.
  - `GET /api/v1/inventory/materials` lists materials with search and active status filters.
  - `GET /api/v1/inventory/materials/{id}` retrieves material details and stock info.
  - `PATCH /api/v1/inventory/materials/{id}` updates material attributes.
  - `DELETE /api/v1/inventory/materials/{id}` deactivates material.
  - Enforces unique `material_code`.
  - Enforces RBAC (`ADMIN`, `INVENTORY_MANAGER`).

### US-INV-002: Stock Level Management & Operations
- **User Story**: As an Inventory Manager, Supervisor, or Production Manager, I want to receive, reserve, release, consume, and adjust material stock so that stock levels reflect shop floor reality.
- **Acceptance Criteria**:
  - `POST /api/v1/inventory/stock/receipt` increases total stock quantity and logs `RECEIPT` movement.
  - `POST /api/v1/inventory/stock/reserve` reserves available stock for Work Orders and logs `RESERVATION` movement.
  - `POST /api/v1/inventory/stock/release` releases reserved stock and logs `RELEASE` movement.
  - `POST /api/v1/inventory/stock/consume` consumes stock during production and logs `CONSUMPTION` movement.
  - `POST /api/v1/inventory/stock/adjust` updates total stock to target audit quantity and logs `ADJUSTMENT` movement.
  - Available quantity is strictly computed as `quantity - reserved_quantity`.
  - Rejects reservations exceeding available stock (returns HTTP 400 Bad Request).
  - Rejects operations on inactive materials (returns HTTP 400 Bad Request).

### US-INV-003: Stock Movement History & Low-Stock Alerts
- **User Story**: As a Supervisor or Inventory Manager, I want to audit movement history and identify low-stock materials.
- **Acceptance Criteria**:
  - `GET /api/v1/inventory/movements` retrieves audit log of stock transactions.
  - `GET /api/v1/inventory/low-stock` identifies active materials where `available_quantity <= reorder_level`.
  - `GET /api/v1/inventory/summary` provides aggregated dashboard summary counts.

### US-INV-004: Inventory Dashboard UI
- **User Story**: As an Inventory Manager or Production User, I want a Next.js interface to manage inventory and view movements.
- **Acceptance Criteria**:
  - Direct navigation route at `/inventory`.
  - Summary cards for Total Materials, Stock Items, Low Stock Warnings, and Reserved Quantity.
  - Interactive modals for creating/editing materials (`CreateMaterialModal`) and recording stock transactions (`StockOperationModal`).
  - Tabs for All Materials, Low Stock Items, and Stock Movement Audit Log.

---

## 🔒 Role-Based Access Control (RBAC) Matrix

| Action / Resource | ADMIN | PRODUCTION_MANAGER | SUPERVISOR | INVENTORY_MANAGER | QUALITY_INSPECTOR | OPERATOR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **View Inventory (`/inventory`)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Get Stock & Movements** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Create/Update Material** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Deactivate Material** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Stock Receipt & Adjustment** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Reserve / Release / Consume** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## 🗄️ Database Architecture & Migrations

- **Alembic Migration**: `backend/alembic/versions/006_add_inventory_materials_and_stock.py`
- **Materials Table (`materials`)**:
  - `id`: `CHAR(36)`, Primary Key
  - `material_code`: `String(50)`, Mandatory, Unique, Indexed
  - `name`: `String(100)`, Mandatory
  - `description`: `Text`, Nullable
  - `unit`: `String(20)`, Mandatory, Default='PCS' (`PCS`, `KG`, `L`, `M`, `OTHER`)
  - `reorder_level`: `Integer`, Mandatory, Default=10
  - `is_active`: `Boolean`, Mandatory, Default=True
  - `created_at`: `DateTime(timezone=True)`, Server Default `now()`
  - `updated_at`: `DateTime(timezone=True)`, Server Default `now()`
- **Inventory Stock Table (`inventory_stocks`)**:
  - `id`: `CHAR(36)`, Primary Key
  - `material_id`: `CHAR(36)`, Foreign Key → `materials.id` (ON DELETE CASCADE), Mandatory, Unique, Indexed
  - `quantity`: `Integer`, Mandatory, Default=0
  - `reserved_quantity`: `Integer`, Mandatory, Default=0
  - `location`: `String(100)`, Mandatory, Default='MAIN-WAREHOUSE'
  - `created_at`: `DateTime(timezone=True)`, Server Default `now()`
  - `updated_at`: `DateTime(timezone=True)`, Server Default `now()`
- **Stock Movements Table (`stock_movements`)**:
  - `id`: `CHAR(36)`, Primary Key
  - `material_id`: `CHAR(36)`, Foreign Key → `materials.id` (ON DELETE CASCADE), Mandatory, Indexed
  - `work_order_id`: `CHAR(36)`, Foreign Key → `work_orders.id` (ON DELETE SET NULL), Nullable, Indexed
  - `movement_type`: `String(50)`, Mandatory (`RECEIPT`, `RESERVATION`, `RELEASE`, `CONSUMPTION`, `ADJUSTMENT`)
  - `quantity`: `Integer`, Mandatory
  - `reference`: `Text`, Nullable
  - `performed_by_id`: `CHAR(36)`, Foreign Key → `users.id` (ON DELETE SET NULL), Nullable
  - `created_at`: `DateTime(timezone=True)`, Server Default `now()`

---

## ✅ Definition of Done (DoD)

- [x] Material, InventoryStock, and StockMovement SQLAlchemy models & Pydantic schemas implemented
- [x] Alembic migration `006_add_inventory_materials_and_stock.py` created
- [x] Material CRUD endpoints (`POST`, `GET`, `PATCH`, `DELETE`) implemented
- [x] Stock transaction APIs (`receipt`, `reserve`, `release`, `consume`, `adjust`) implemented & validated
- [x] Available quantity math (`quantity - reserved_quantity`) strictly computed
- [x] Low-stock detection API (`/api/v1/inventory/low-stock`) and summary API implemented
- [x] RBAC rules enforced (`INVENTORY_MANAGER` primary role, `OPERATOR`/`QUALITY` read-only)
- [x] Pytest test suite expanded to 101 tests (`test_sprint7_inventory.py`, 100% pass rate)
- [x] Dedicated Next.js Inventory Dashboard (`/inventory`) implemented with modals (`CreateMaterialModal`, `StockOperationModal`)
- [x] Header Navigation updated (`AppHeaderNav.tsx`)
- [x] `npm run build` passes with zero linting or type errors
- [x] Agile documentation created in `docs/agile/sprint_7.md`
