# SmartMES - Sprint 6 Documentation: Quality Inspection & Quality Control Module

## 🎯 Sprint Goal
Implement a complete Quality Inspection and Quality Control module for SmartMES. The module enables quality inspectors, supervisors, and production managers to conduct post-production inspections on `COMPLETED` work orders, record accepted/rejected quantities, manage detailed defect entries with categories and severities, update quality verdict statuses (`PENDING`, `PASSED`, `FAILED`, `REWORK_REQUIRED`), track aggregated quality metrics via a dedicated Next.js Quality Dashboard (`/quality`), enforce strict business rules and RBAC permissions, and integrate quality status visibility into Work Orders and Shop Floor terminals.

---

## 📋 User Stories & Acceptance Criteria

### US-QC-001: Quality Inspection Workflow
- **User Story**: As a Quality Inspector or Production Manager, I want to conduct quality inspections on completed work orders so that production output is verified before release.
- **Acceptance Criteria**:
  - `POST /api/v1/quality/inspections` creates an inspection record for `COMPLETED` work orders.
  - `GET /api/v1/quality/inspections` lists inspections with optional status filtering.
  - `GET /api/v1/quality/inspections/{id}` retrieves full inspection details including nested defects.
  - `PATCH /api/v1/quality/inspections/{id}` updates inspection quantities, status (`PENDING`, `PASSED`, `FAILED`, `REWORK_REQUIRED`), and remarks.
  - Re-inspection is permitted for `REWORK_REQUIRED` work orders.
  - Enforces RBAC permissions (`ADMIN`, `PRODUCTION_MANAGER`, `SUPERVISOR`, `QUALITY_INSPECTOR`).
  - Logs audit events (`QUALITY_INSPECTION_CREATED`, `QUALITY_INSPECTION_UPDATED`).

### US-QC-002: Defect Management
- **User Story**: As a Quality Inspector, I want to log, categorize, and update defect records during inspection so that defect causes and severities are documented.
- **Acceptance Criteria**:
  - `POST /api/v1/quality/inspections/{id}/defects` records a defect entry with type (`DIMENSIONAL`, `SURFACE`, `MATERIAL`, `ASSEMBLY`, `FUNCTIONAL`, `COSMETIC`, `OTHER`), severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), description, quantity, and remarks.
  - `GET /api/v1/quality/inspections/{id}/defects` lists recorded defects for an inspection.
  - `PATCH /api/v1/quality/defects/{id}` updates defect attributes.
  - `DELETE /api/v1/quality/defects/{id}` deletes a defect entry.
  - Logs audit events (`QUALITY_DEFECT_CREATED`, `QUALITY_DEFECT_UPDATED`, `QUALITY_DEFECT_DELETED`).

### US-QC-003: Quality Metrics & Summary Dashboard
- **User Story**: As a Production Manager or Supervisor, I want to view aggregated quality metrics so that defect trends and rejection rates are monitored.
- **Acceptance Criteria**:
  - `GET /api/v1/quality/summary` returns total inspections, status breakdowns, total rejected quantity, and total defect counts.
  - Dedicated Next.js route at `/quality` displaying summary cards, filtering, inspection log table, and modals for creating inspections and managing defects.

### US-QC-004: Work Order & Shop Floor Quality Integration
- **User Story**: As an Operator or Supervisor, I want to view the current quality status on Work Orders and Shop Floor terminals.
- **Acceptance Criteria**:
  - Work Order responses include `quality_status` dynamically computed from latest inspection.
  - Work Order list (`/work-orders`) displays Quality Status badge alongside production status for completed work orders.
  - Shop Floor terminal (`/shop-floor`) displays Quality Status badge on completed work order cards.

---

## 🔒 Role-Based Access Control (RBAC) Matrix

| Action / Resource | ADMIN | PRODUCTION_MANAGER | SUPERVISOR | QUALITY_INSPECTOR | OPERATOR | INVENTORY_MANAGER |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **View Quality Dashboard (`/quality`)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Get Inspection Summary (`/quality/summary`)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **List/View Inspections & Defects** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Create/Update Inspection** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Add/Edit/Delete Defects** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## 🗄️ Database Architecture & Migrations

- **Alembic Migration**: `backend/alembic/versions/005_add_quality_inspection_and_defects.py`
- **Quality Inspections Table (`quality_inspections`)**:
  - `id`: `CHAR(36)`, Primary Key
  - `work_order_id`: `CHAR(36)`, Foreign Key → `work_orders.id` (ON DELETE CASCADE), Mandatory, Indexed
  - `inspector_id`: `CHAR(36)`, Foreign Key → `users.id` (ON DELETE SET NULL), Nullable, Indexed
  - `inspected_quantity`: `Integer`, Mandatory, Default=0
  - `accepted_quantity`: `Integer`, Mandatory, Default=0
  - `rejected_quantity`: `Integer`, Mandatory, Default=0
  - `status`: `String(50)`, Mandatory, Default='PENDING' (`PENDING`, `PASSED`, `FAILED`, `REWORK_REQUIRED`)
  - `remarks`: `Text`, Nullable
  - `inspection_date`: `DateTime(timezone=True)`, Mandatory, Server Default `now()`
  - `created_at`: `DateTime(timezone=True)`, Mandatory, Server Default `now()`
  - `updated_at`: `DateTime(timezone=True)`, Mandatory, Server Default `now()`
- **Quality Defects Table (`quality_defects`)**:
  - `id`: `CHAR(36)`, Primary Key
  - `inspection_id`: `CHAR(36)`, Foreign Key → `quality_inspections.id` (ON DELETE CASCADE), Mandatory, Indexed
  - `defect_type`: `String(50)`, Mandatory, Default='OTHER' (`DIMENSIONAL`, `SURFACE`, `MATERIAL`, `ASSEMBLY`, `FUNCTIONAL`, `COSMETIC`, `OTHER`)
  - `severity`: `String(20)`, Mandatory, Default='MEDIUM' (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
  - `description`: `Text`, Nullable
  - `quantity`: `Integer`, Mandatory, Default=1
  - `remarks`: `Text`, Nullable
  - `created_at`: `DateTime(timezone=True)`, Mandatory, Server Default `now()`
  - `updated_at`: `DateTime(timezone=True)`, Mandatory, Server Default `now()`

---

## ✅ Definition of Done (DoD)

- [x] QualityInspection and QualityDefect SQLAlchemy models & Pydantic schemas implemented
- [x] Alembic migration `005_add_quality_inspection_and_defects.py` created
- [x] Inspection CRUD & validation rules implemented (completed work order check, quantity bounds check)
- [x] Defect management CRUD endpoints (`POST`, `GET`, `PATCH`, `DELETE`) implemented
- [x] Quality summary aggregation API implemented (`/api/v1/quality/summary`)
- [x] RBAC permissions enforced (`QUALITY_INSPECTOR` primary role, `OPERATOR`/`INVENTORY` read-only)
- [x] Pytest test suite expanded to 94 tests (`test_sprint6_quality.py`, 100% pass rate)
- [x] Dedicated Next.js Quality Dashboard (`/quality`) implemented with modals (`CreateInspectionModal`, `InspectionDetailModal`)
- [x] Header Navigation updated (`AppHeaderNav.tsx`)
- [x] Quality status integrated on Work Order Management (`/work-orders`) and Shop Floor Terminal (`/shop-floor`)
- [x] `npm run build` passes with zero linting or type errors
- [x] Agile documentation created in `docs/agile/sprint_6.md`
