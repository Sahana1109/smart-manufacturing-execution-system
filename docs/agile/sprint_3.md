# SmartMES - Sprint 3 Documentation: Work Order Management Module

## 🎯 Sprint Goal
Implement the Work Order Management module, bridging production plans with shop-floor manufacturing execution. The module enables creating work orders derived from production plans, assigning machinery and operators, enforcing a 7-stage status lifecycle state machine (`DRAFT -> RELEASED -> IN_PROGRESS <-> PAUSED -> COMPLETED -> CLOSED`), recording enterprise audit events, and providing a responsive Next.js work orders dashboard.

---

## 📋 User Stories & Acceptance Criteria

### US-WO-001: Create Work Order
- **User Story**: As a Production Manager, I want to create a work order linked to an existing production plan so that execution tasks can be dispatched.
- **Acceptance Criteria**:
  - `planned_quantity` > 0.
  - `due_date` >= `start_date`.
  - Production Plan must exist.
  - Selected Product must exist and be active (`is_active = true`).
  - Auto-generates unique `work_order_number` if omitted.
  - Returns HTTP 201 Created and logs `WORK_ORDER_CREATED` audit event.

### US-WO-002: View & Filter Work Orders
- **User Story**: As an authorized user, I want to list and filter work orders by status, priority, production plan, product, and search terms so that I can monitor execution progress.
- **Acceptance Criteria**:
  - `GET /api/v1/work-orders` supports `status`, `priority`, `production_plan_id`, `product_id`, and `search` filters.
  - Supports pagination parameters (`page`, `limit`).

### US-WO-003: Work Order Status State Machine
- **User Story**: As an operator or supervisor, I want to transition work order status through valid lifecycle stages (including pause/resume).
- **Acceptance Criteria**:
  - Valid status transitions enforced (`DRAFT -> RELEASED -> IN_PROGRESS <-> PAUSED -> COMPLETED -> CLOSED`).
  - Operators can update execution status (`IN_PROGRESS`, `PAUSED`, `COMPLETED`).
  - Invalid transitions return HTTP 400 Bad Request.
  - Records `WORK_ORDER_STATUS_CHANGED` audit log event.

### US-WO-004: Machine & Operator Assignment
- **User Story**: As a Supervisor or Production Manager, I want to assign active machines and operators to work orders.
- **Acceptance Criteria**:
  - `PATCH /api/v1/work-orders/{id}/assign` updates `assigned_machine_id` and `assigned_employee_id`.
  - Assigned machine/employee must exist and be active.
  - Records audit events `WORK_ORDER_MACHINE_ASSIGNED` and `WORK_ORDER_EMPLOYEE_ASSIGNED`.

---

## ✅ Definition of Done (DoD)

- [x] Machine, Employee, and WorkOrder SQLAlchemy models created
- [x] Alembic migration `003_create_work_orders_machines_and_employees.py` generated
- [x] Service layer business logic & state machine validation implemented
- [x] Audit logging integrated (`WORK_ORDER_*` audit events)
- [x] REST API endpoints (`POST`, `GET`, `PUT`, `PATCH /status`, `PATCH /assign`, `POST /cancel`) implemented
- [x] RBAC dependencies integrated (`require_roles`)
- [x] Pytest test suite `test_work_orders.py` (25 scenarios) implemented and 100% passing
- [x] All 39 existing Sprint 1 & 2 tests continue passing (64+ tests total)
- [x] Next.js frontend Dashboard list, Create Modal, Details/Status Modal, Assign Modal implemented
- [x] `npm run build` passes with zero type/lint errors
- [x] Documentation updated in `docs/`
