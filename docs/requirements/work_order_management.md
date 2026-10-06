# SmartMES - SRS: Work Order Management Module

## 1. Problem Statement & Business Overview
Work Order Management connects high-level Production Planning with shop-floor manufacturing execution. A Work Order represents a discrete, actionable manufacturing task derived from an approved Production Plan. It defines the target quantity, product specification, start and due dates, machine assignment, and assigned operator while tracking state transitions across the manufacturing workflow.

---

## 2. Domain Specifications

### 2.1 Supporting Entities
- **Machine**: `id` (UUID), `machine_code` (Unique String), `name` (String), `status` (String, e.g., OPERATIONAL, IDLE, MAINTENANCE), `is_active` (Boolean).
- **Employee**: `id` (UUID), `employee_code` (Unique String), `first_name` (String), `last_name` (String), `role_title` (String), `is_active` (Boolean).

### 2.2 Work Order Entity
- **Attributes**:
  - `id`: UUID (Primary Key)
  - `work_order_number`: Unique String (Format: `WO-YYYY-XXXX`)
  - `production_plan_id`: FK -> production_plans.id (Not Null)
  - `product_id`: FK -> products.id (Not Null)
  - `planned_quantity`: Positive Integer (> 0)
  - `start_date`: Date / Timestamp
  - `due_date`: Date / Timestamp
  - `priority`: Enum (`LOW`, `MEDIUM`, `HIGH`, `URGENT`, Default: `MEDIUM`)
  - `status`: Enum (`DRAFT`, `RELEASED`, `IN_PROGRESS`, `PAUSED`, `COMPLETED`, `CLOSED`, `CANCELLED`, Default: `DRAFT`)
  - `notes`: Text
  - `created_by_id`: FK -> users.id
  - `assigned_machine_id`: FK -> machines.id (Nullable)
  - `assigned_employee_id`: FK -> employees.id (Nullable)
  - `created_at` & `updated_at`: UTC Timestamps

---

## 3. Status Lifecycle State Machine

```
   +--------+           +----------+           +-------------+           +-----------+           +--------+
   | DRAFT  | --------> | RELEASED | --------> | IN_PROGRESS | --------> | COMPLETED | --------> | CLOSED |
   +--------+           +----------+           +-------------+           +-----------+           +--------+
        |                    |                     ^     |
        |                    |                     |     v
        |                    |                 +-------------+
        |                    |                 |   PAUSED    |
        |                    |                 +-------------+
        |                    |                        |
        +--------------------+------------------------+----------------------> [ CANCELLED ]
```

### Transition Validation Rules
- **`DRAFT` -> `RELEASED`**: Work order dispatched to shop floor.
- **`RELEASED` -> `IN_PROGRESS`**: Operator commences execution on assigned machine.
- **`IN_PROGRESS` <-> `PAUSED`**: Paused for shift change, tool maintenance, or raw material supply.
- **`IN_PROGRESS` -> `COMPLETED`**: Work order target quantity produced.
- **`COMPLETED` -> `CLOSED`**: Work order administratively closed.
- **`DRAFT` / `RELEASED` / `IN_PROGRESS` / `PAUSED` -> `CANCELLED`**: Cancelled by production management.
- **Invalid Transitions**: Any transition not explicitly listed returns HTTP 400 Bad Request.

---

## 4. Role-Based Access Control (RBAC) Matrix

| Operation | ADMIN | PRODUCTION_MANAGER | SUPERVISOR | OPERATOR | QUALITY_INSPECTOR | INVENTORY_MANAGER |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Create Work Order** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **List/View Orders** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Update Details** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Assign Machine/Operator** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Status Transition** | ✅ | ✅ | ✅ | ✅ (Execution only) | ❌ | ❌ |
| **Cancel Work Order** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
