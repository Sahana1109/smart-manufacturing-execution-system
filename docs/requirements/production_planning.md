# SmartMES - SRS: Production Planning Module

## 1. Problem Statement & Business Overview
Production Planning is the foundational manufacturing workflow in SmartMES. A Production Plan defines the planned manufacturing output for a specific product SKU during a target time window. It establishes demand targets, scheduling parameters, priority rankings, and lifecycle states before work orders are dispatched to shop-floor machinery.

---

## 2. Domain Specifications

### 2.1 Product Entity
- **Attributes**: `id` (UUID), `product_code` (Unique String), `name` (String), `description` (Text), `unit_of_measure` (String, e.g., PCS, KG, METERS), `is_active` (Boolean).
- **Business Rule**: Products must be active (`is_active = true`) to be scheduled on a production plan.

### 2.2 Production Plan Entity
- **Attributes**:
  - `id`: UUID (Primary Key)
  - `plan_number`: Unique String (Format: `PP-YYYY-XXXX`)
  - `product_id`: FK -> products.id
  - `planned_quantity`: Positive Integer (> 0)
  - `start_date`: Date / Timestamp
  - `due_date`: Date / Timestamp
  - `priority`: Enum (`LOW`, `MEDIUM`, `HIGH`, `URGENT`, Default: `MEDIUM`)
  - `status`: Enum (`DRAFT`, `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, Default: `DRAFT`)
  - `notes`: Text
  - `created_by_id`: FK -> users.id
  - `created_at` & `updated_at`: UTC Timestamps

---

## 3. Status Lifecycle State Machine

```
   +--------+           +---------+           +-------------+           +-----------+
   | DRAFT  | --------> | PLANNED | --------> | IN_PROGRESS | --------> | COMPLETED |
   +--------+           +---------+           +-------------+           +-----------+
        |                    |                      |
        +--------------------+----------------------+ --------> [ CANCELLED ]
```

### Transition Validation Rules
- **`DRAFT` -> `PLANNED`**: Plan approved for scheduling.
- **`PLANNED` -> `IN_PROGRESS`**: Execution begun on shop floor.
- **`IN_PROGRESS` -> `COMPLETED`**: Planned production quantity fulfilled.
- **`DRAFT` / `PLANNED` / `IN_PROGRESS` -> `CANCELLED`**: Allowed when order is revoked.
- **Invalid Transitions**: `COMPLETED -> DRAFT`, `CANCELLED -> IN_PROGRESS`, etc. return HTTP 400 Bad Request.

---

## 4. Role-Based Access Control (RBAC) Matrix

| Operation | ADMIN | PRODUCTION_MANAGER | SUPERVISOR | OPERATOR | QUALITY_INSPECTOR | INVENTORY_MANAGER |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Create Plan** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **List/View Plans**| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Update Details** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Change Status**  | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Cancel Plan**    | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
