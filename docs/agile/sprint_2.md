# SmartMES - Sprint 2 Documentation: Production Planning Module

## 🎯 Sprint Goal
Implement the core Production Planning domain module, enabling production managers and authorized shop-floor users to create, schedule, monitor, filter, update, and manage the lifecycle state of production plans while maintaining strict business validations, RBAC authorization, audit logging, and responsive Next.js user interfaces.

---

## 📋 User Stories & Acceptance Criteria

### US-PP-001: Create Production Plan
- **User Story**: As a Production Manager, I want to create a production plan specifying product, quantity, target dates, and priority so that manufacturing schedules can be established.
- **Acceptance Criteria**:
  - `planned_quantity` > 0.
  - `due_date` >= `start_date`.
  - Selected product must exist and be active (`is_active = true`).
  - Auto-generates unique `plan_number` if omitted.
  - Returns HTTP 201 Created and logs an audit event.

### US-PP-002: View & Filter Production Plans
- **User Story**: As an authorized user, I want to view and filter production plans by status, priority, and product so that I can quickly locate relevant schedules.
- **Acceptance Criteria**:
  - `GET /api/v1/production-plans` supports `status`, `priority`, `product_id`, and `search` filters.
  - Supports pagination parameters (`page`, `limit`).

### US-PP-003: Update Production Plan & Status Transitions
- **User Story**: As a Production Manager or Supervisor, I want to update plan notes and advance plan status through valid lifecycle stages.
- **Acceptance Criteria**:
  - Valid status transitions enforced (`DRAFT -> PLANNED -> IN_PROGRESS -> COMPLETED`).
  - Invalid transitions return HTTP 400 Bad Request.
  - Records audit log entry upon status change.

### US-PP-004: Role-Based Authorization
- **User Story**: As an Admin, I want production planning actions restricted by RBAC permissions.
- **Acceptance Criteria**:
  - Plan creation and cancellation restricted to `ADMIN` and `PRODUCTION_MANAGER`.
  - Read-only access enforced for operators, quality inspectors, and inventory managers.

---

## ✅ Definition of Done (DoD)

- [x] Product & ProductionPlan SQLAlchemy models created
- [x] Alembic migration `002_create_products_production_plans_and_audit_logs.py` generated
- [x] Service layer business logic & state machine validation implemented
- [x] Audit logging integrated (`AuditLog` entity & `log_audit_event`)
- [x] REST API endpoints (`POST`, `GET`, `PUT`, `PATCH /status`, `POST /cancel`) implemented
- [x] RBAC dependencies integrated (`require_roles`)
- [x] Pytest test suite `test_production_planning.py` (20 scenarios) implemented and 100% passing
- [x] Next.js frontend Dashboard list, Create Modal, Details/Status Modal implemented
- [x] `npm run build` passes with zero type/lint errors
- [x] Documentation updated in `docs/`
