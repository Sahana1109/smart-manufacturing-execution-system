# SmartMES - Database & Migration Guidelines

## 1. Overview
SmartMES uses **PostgreSQL 16** as its relational database management system, managed via **SQLAlchemy 2.0 ORM** and **Alembic** schema migration framework.

---

## 2. Naming Conventions & Rules

- **Tables**: Snake_case, plural nouns (e.g., `users`, `work_orders`, `machines`, `audit_logs`).
- **Columns**: Snake_case, singular (e.g., `id`, `work_order_code`, `status`, `created_at`).
- **Primary Keys**: UUID or BigInteger named `id`.
- **Foreign Keys**: `referenced_table_singular_id` (e.g., `user_id`, `machine_id`, `work_order_id`).
- **Timestamps**: UTC timestamp columns `created_at` and `updated_at` on all domain tables.

---

## 3. Migration Strategy

1. All schema changes MUST be executed through Alembic migrations located in `backend/alembic/versions/`.
2. Direct `CREATE TABLE` or `ALTER TABLE` execution in production databases is strictly prohibited.
3. Every migration file must include both `upgrade()` and `downgrade()` procedures.

---

## 4. Initial Database Setup Script

A lightweight database initialization script is provided in `database/init.sql` to establish database users, extensions (such as `uuid-ossp`), and initial database creation for local Docker execution.
