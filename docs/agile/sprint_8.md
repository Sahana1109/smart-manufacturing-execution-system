# SmartMES - Sprint 8 Documentation: Reports & Management Dashboards Module

## 🎯 Sprint Goal
Implement a complete Reports & Management Dashboards module for SmartMES. The module consolidates operational metrics across Work Orders, Production Execution, Quality Control, Inventory & Material Tracking, Machine Maintenance/Utilization, and Workforce/Operator Allocations. Management can view real-time KPIs, analyze performance breakdowns, filter by date range (`from_date`, `to_date`), export tabular reports to CSV, and access domain-specific views via a dedicated Next.js Management Dashboard at `/dashboard`.

---

## 📋 User Stories & Acceptance Criteria

### US-REP-001: Consolidated Management Dashboard
- **User Story**: As a Management User, Admin, or Manager, I want a high-level executive dashboard showing core KPIs across all operational domains so that I can evaluate MES performance.
- **Acceptance Criteria**:
  - `GET /api/v1/reports/dashboard` returns consolidated summary metrics for Production, Quality, Inventory, Machines, and Operators.
  - Supports optional date filtering (`from_date`, `to_date`).
  - Next.js UI route at `/dashboard` presents Row 1 (Overall KPIs), Row 2 (Production Execution), Row 3 (Quality Inspection), Row 4 (Machines Status), and Row 5 (Inventory & Low Stock).

### US-REP-002: Production Execution Report
- **User Story**: As a Production Manager or Supervisor, I want a production report detailing work order counts, status breakdowns, planned vs produced quantities, and completion percentages.
- **Acceptance Criteria**:
  - `GET /api/v1/reports/production` computes total work orders, pending, in progress, paused, completed, closed, and cancelled counts.
  - Computes `completion_percentage` (`completed / total_work_orders * 100`).
  - Sums total planned quantity and total produced quantity.
  - Supports CSV export (`SmartMES_Production_Report.csv`).

### US-REP-003: Quality Control Report
- **User Story**: As a Quality Inspector or Production Manager, I want a quality summary report detailing inspection outcomes, defect counts, and rejected quantities.
- **Acceptance Criteria**:
  - `GET /api/v1/reports/quality` computes inspection status breakdown (passed, failed, rework required, pending).
  - Calculates total inspected, accepted, and rejected quantities.
  - Sums total defect count across `QualityDefect` records.
  - Supports CSV export (`SmartMES_Quality_Report.csv`).

### US-REP-004: Inventory & Material Report
- **User Story**: As an Inventory Manager or Admin, I want an inventory report summarizing material counts, stock totals, low-stock items, and recent audit movements.
- **Acceptance Criteria**:
  - `GET /api/v1/reports/inventory` calculates total materials, total stock items, total quantity, reserved quantity, and available quantity.
  - Identifies low-stock items where `available_quantity <= reorder_level`.
  - Provides recent stock movement audit trail.
  - Supports CSV export (`SmartMES_Low_Stock_Report.csv`).

### US-REP-005: Machine Status Report
- **User Story**: As a Supervisor or Production Manager, I want a machine status report to inspect machine availability and maintenance states.
- **Acceptance Criteria**:
  - `GET /api/v1/reports/machines` returns machine counts broken down by status: Operational, In Use, Maintenance, and Inactive.

### US-REP-006: Operator & Workforce Summary
- **User Story**: As a Supervisor or Production Manager, I want an operator summary report showing workforce allocation.
- **Acceptance Criteria**:
  - `GET /api/v1/reports/operators` returns total operators, active operators, assigned operators (on active work orders), and available operators.

---

## 🔒 Role-Based Access Control (RBAC) Matrix

| Report / Endpoint | ADMIN | PRODUCTION_MANAGER | SUPERVISOR | QUALITY_INSPECTOR | INVENTORY_MANAGER | OPERATOR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`/api/v1/reports/dashboard`** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **`/api/v1/reports/production`** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **`/api/v1/reports/quality`** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **`/api/v1/reports/inventory`** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **`/api/v1/reports/machines`** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **`/api/v1/reports/operators`** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Frontend `/dashboard` Access** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🗄️ Backend API Specifications

- **Router Base Path**: `/api/v1/reports`
- **Schemas**: Defined in `backend/app/modules/reports/schemas.py` (`ProductionReportResponse`, `QualityReportResponse`, `InventoryReportResponse`, `MachineReportResponse`, `OperatorReportResponse`, `DashboardSummaryResponse`).
- **Service**: Implemented in `backend/app/modules/reports/service.py` using fast, non-blocking async aggregate queries.
- **Date Range Validation**: Rejects invalid query filters where `from_date > to_date` with HTTP 400 Bad Request.

---

## ✅ Definition of Done (DoD)

- [x] Backend report schemas (`schemas.py`) and aggregation services (`service.py`) implemented
- [x] Report APIs (`/dashboard`, `/production`, `/quality`, `/inventory`, `/machines`, `/operators`) created and registered
- [x] Date filtering validation (`from_date`, `to_date`) implemented and tested
- [x] RBAC access rules configured and verified across all 6 system roles
- [x] Dedicated Next.js Management Dashboard (`/dashboard`) created with Tab views, KPI cards, visual progress meters, and CSV export functionality
- [x] Header Navigation updated (`AppHeaderNav.tsx`) with `/dashboard` link
- [x] Pytest backend test suite created (`test_sprint8_reports.py`) and full suite verified (105/105 tests passing)
- [x] `npm run build` passes with zero errors (`/dashboard` compiled static page)
- [x] Agile documentation created in `docs/agile/sprint_8.md`
