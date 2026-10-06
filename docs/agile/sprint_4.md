# SmartMES - Sprint 4 Documentation: Machine & Operator Assignment Module

## 🎯 Sprint Goal
Implement a complete Machine and Employee/Operator Management & Assignment module for SmartMES. The module enables creating and managing machinery and operator directories, setting operational and maintenance statuses, assigning eligible resources to active work orders, enforcing availability & RBAC rules, auto-synchronizing machine execution statuses, and providing dedicated Next.js management dashboards.

---

## 📋 User Stories & Acceptance Criteria

### US-MA-001: Machine Catalog Management
- **User Story**: As a Production Manager or Supervisor, I want to create and manage shop-floor machinery so that machine availability can be tracked.
- **Acceptance Criteria**:
  - `POST /api/v1/machines` creates machine entity with code, name, and status (`OPERATIONAL`, `AVAILABLE`, `MAINTENANCE`, `INACTIVE`).
  - `PUT /api/v1/machines/{id}` updates machine properties.
  - `PATCH /api/v1/machines/{id}/status` transitions status.
  - `DELETE /api/v1/machines/{id}` soft-deletes/deactivates machine.
  - Enforces RBAC (`ADMIN`, `PRODUCTION_MANAGER`, `SUPERVISOR`).
  - Logs audit events (`MACHINE_CREATED`, `MACHINE_UPDATED`, `MACHINE_STATUS_CHANGED`, `MACHINE_DEACTIVATED`).

### US-EM-001: Operator Directory Management
- **User Story**: As a Production Manager, I want to manage employee/operator personnel details so that execution assignments can be allocated.
- **Acceptance Criteria**:
  - `POST /api/v1/employees` creates operator entity.
  - `PUT /api/v1/employees/{id}` updates employee details.
  - `DELETE /api/v1/employees/{id}` soft-deletes employee.
  - Enforces RBAC (`ADMIN`, `PRODUCTION_MANAGER`).
  - Logs audit events (`EMPLOYEE_CREATED`, `EMPLOYEE_UPDATED`, `EMPLOYEE_DEACTIVATED`).

### US-WO-005: Resource Assignment & Validation
- **User Story**: As a Supervisor or Production Manager, I want to assign available machines and eligible operators to work orders while preventing invalid assignments.
- **Acceptance Criteria**:
  - `PATCH /api/v1/work-orders/{id}/assign` assigns machine/employee.
  - Validates that assigned machine is not in `MAINTENANCE` or `INACTIVE` state (returns HTTP 400 Bad Request).
  - Validates that target work order is active (returns HTTP 400 for `COMPLETED`, `CLOSED`, `CANCELLED`).
  - Auto-synchronizes machine status to `IN_USE` when work order enters `IN_PROGRESS`.
  - Restores machine status to `OPERATIONAL` when work order completes, pauses, or cancels.
  - `DELETE /api/v1/work-orders/{id}/assign/machine` and `/employee` unassign resources.
  - Logs audit events (`WORK_ORDER_MACHINE_ASSIGNED`, `WORK_ORDER_EMPLOYEE_ASSIGNED`, `WORK_ORDER_MACHINE_UNASSIGNED`, `WORK_ORDER_EMPLOYEE_UNASSIGNED`).

---

## 🔒 Role-Based Access Control (RBAC) Matrix

| Action / Resource | ADMIN | PRODUCTION_MANAGER | SUPERVISOR | OPERATOR | QUALITY_INSPECTOR | INVENTORY_MANAGER |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **List/View Machines** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Create/Update Machine** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Deactivate Machine** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **List/View Operators** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Create/Update Operator** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Assign/Unassign Resources**| ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## ✅ Definition of Done (DoD)

- [x] Machine and Employee CRUD APIs & services implemented
- [x] Machine maintenance status validation & auto-sync implemented
- [x] Work order unassignment APIs implemented
- [x] Audit logging integrated (`MACHINE_*`, `EMPLOYEE_*`, `WORK_ORDER_*_UNASSIGNED`)
- [x] RBAC dependencies integrated across endpoints
- [x] Pytest test suite expanded (14 new scenarios in `test_sprint4_assignments.py`, 79 tests total passing 100%)
- [x] Next.js Machine Management UI (`/machines`) implemented
- [x] Next.js Operator Directory UI (`/employees`) implemented
- [x] Next.js Header Navigation updated (`AppHeaderNav.tsx`)
- [x] `npm run build` passes with zero type/lint errors
- [x] Agile documentation updated in `docs/agile/sprint_4.md`
