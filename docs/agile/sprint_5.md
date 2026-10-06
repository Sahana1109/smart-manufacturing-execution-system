# SmartMES - Sprint 5 Documentation: Production Execution / Shop Floor Module

## 🎯 Sprint Goal
Implement the complete Production Execution and Shop Floor module for SmartMES. The module enables operators and authorized production personnel to execute assigned work orders through a controlled production lifecycle (`PENDING` → `IN_PROGRESS` ↔ `PAUSED` → `COMPLETED`), track real-time quantity progress, record downtime and operational delays, maintain machine status synchronization (`IN_USE` vs `OPERATIONAL`), enforce strict business rules and RBAC permissions, and operate via a dedicated Next.js Shop Floor Terminal (`/shop-floor`).

---

## 📋 User Stories & Acceptance Criteria

### US-PE-001: Production Lifecycle Execution
- **User Story**: As an Operator or Production Manager, I want to start, pause, resume, and complete work orders so that shop floor operations are accurately recorded.
- **Acceptance Criteria**:
  - `POST /api/v1/work-orders/{id}/start` sets status to `IN_PROGRESS`, records `actual_start_time`, and synchronizes assigned machine status to `IN_USE`.
  - `POST /api/v1/work-orders/{id}/pause` sets status to `PAUSED` with reason and restores assigned machine status to `OPERATIONAL`.
  - `POST /api/v1/work-orders/{id}/resume` returns status to `IN_PROGRESS` and sets machine back to `IN_USE`.
  - `POST /api/v1/work-orders/{id}/complete` sets status to `COMPLETED`, records `actual_completion_time`, updates final `produced_quantity`, and restores machine status to `OPERATIONAL`.
  - Enforces RBAC permissions (`ADMIN`, `PRODUCTION_MANAGER`, `SUPERVISOR`, `OPERATOR`).
  - Logs audit events (`WORK_ORDER_STARTED`, `WORK_ORDER_PAUSED`, `WORK_ORDER_RESUMED`, `WORK_ORDER_COMPLETED`).

### US-PE-002: Production Quantity & Progress Tracking
- **User Story**: As a Supervisor or Operator, I want to track produced quantities against target quantities so that completion percentages and remaining units are visible.
- **Acceptance Criteria**:
  - Work Order model includes `produced_quantity`, `remaining_quantity` (computed), and `progress_percentage` (computed).
  - Validation prevents negative produced quantities and enforces target quantity bounds unless overproduction is explicitly allowed.
  - Complete work order endpoint records final produced quantity and updates progress to 100%.

### US-PE-003: Shop Floor Downtime & Delay Recording
- **User Story**: As an Operator or Supervisor, I want to record machine breakdowns and operational delays so that downtime causes and durations are tracked.
- **Acceptance Criteria**:
  - `POST /api/v1/work-orders/{id}/downtime` records downtime entries with `category` (`MACHINE_BREAKDOWN`, `MATERIAL_UNAVAILABLE`, `OPERATOR_UNAVAILABLE`, `MAINTENANCE`, `POWER_FAILURE`, `OTHER`), `start_time`, `end_time`, `duration_minutes`, and `remarks`.
  - `GET /api/v1/work-orders/{id}/downtime` retrieves downtime history for a work order.
  - Automatically associates relevant machine and recording user.
  - Logs audit event `DOWNTIME_RECORDED`.

### US-PE-004: Shop Floor Terminal UI & Execution Detail
- **User Story**: As a Shop Floor Operator or Supervisor, I want a streamlined Next.js dashboard to view active work orders and trigger execution actions.
- **Acceptance Criteria**:
  - Direct navigation route at `/shop-floor`.
  - Quick action buttons (Start, Pause, Resume, Complete, Record Downtime) conditioned on current status and user permissions.
  - Interactive modals for completion quantity entry and downtime reporting.
  - Real-time progress bars, resource tags, and status indicators.

---

## 🔒 Role-Based Access Control (RBAC) Matrix

| Action / Resource | ADMIN | PRODUCTION_MANAGER | SUPERVISOR | OPERATOR | QUALITY_INSPECTOR | INVENTORY_MANAGER |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **View Shop Floor Terminal** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Start Production** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Pause Production** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Resume Production** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Complete Production** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Record Downtime** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **View Downtime History** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🗄️ Database Architecture & Migrations

- **Alembic Migration**: `backend/alembic/versions/004_add_production_execution_and_downtime.py`
- **Work Orders Table Updates**:
  - `actual_start_time`: `DateTime(timezone=True)`, Nullable
  - `actual_completion_time`: `DateTime(timezone=True)`, Nullable
  - `produced_quantity`: `Integer`, Default=0
- **Downtime Records Table**:
  - `id`: `Integer`, Primary Key
  - `work_order_id`: `Integer`, Foreign Key → `work_orders.id` (ON DELETE CASCADE)
  - `machine_id`: `Integer`, Foreign Key → `machines.id` (Nullable)
  - `recorded_by_id`: `Integer`, Foreign Key → `users.id` (Nullable)
  - `category`: `String(50)`, Mandatory
  - `start_time`: `DateTime(timezone=True)`, Mandatory
  - `end_time`: `DateTime(timezone=True)`, Nullable
  - `duration_minutes`: `Integer`, Default=0
  - `remarks`: `Text`, Nullable
  - `created_at`: `DateTime(timezone=True)`, Server Default `now()`

---

## ✅ Definition of Done (DoD)

- [x] Work Order execution state transitions (`start`, `pause`, `resume`, `complete`) implemented & validated
- [x] Quantity progress & percentage tracking implemented
- [x] Downtime recording & retrieval APIs implemented (`/downtime`)
- [x] Machine status auto-synchronization (`IN_USE` vs `OPERATIONAL`) preserved and extended
- [x] RBAC enforcement integrated across all execution and downtime endpoints
- [x] Pytest suite expanded to 86 tests (7 new execution scenarios in `test_sprint5_execution.py`, 100% pass rate)
- [x] Dedicated Next.js Shop Floor Terminal (`/shop-floor`) implemented with modals
- [x] Header Navigation updated (`AppHeaderNav.tsx`)
- [x] `npm run build` passes with zero linting or type errors
- [x] Agile documentation created in `docs/agile/sprint_5.md`
