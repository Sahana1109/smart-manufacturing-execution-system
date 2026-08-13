# SmartMES - System Architecture Specification

## 1. Architectural Overview

SmartMES follows a **Modular Monolith** architecture pattern. This design balances operational simplicity, rapid local development, and clean domain boundaries.

```
+-----------------------------------------------------------------------+
|                         Next.js 14+ Frontend                          |
|             (App Router, TypeScript, Tailwind CSS UI)                 |
+-----------------------------------------------------------------------+
                                   |
                             REST / JSON APIs
                                   |
+-----------------------------------------------------------------------+
|                           FastAPI Backend                             |
|                                                                       |
|  +--------------+  +--------------+  +--------------+  +-----------+  |
|  | Auth & Users |  | Master Data  |  |  Inventory   |  | Work      |  |
|  | Module       |  | Module       |  |  Module      |  | Orders    |  |
|  +--------------+  +--------------+  +--------------+  +-----------+  |
|  +--------------+  +--------------+  +--------------+  +-----------+  |
|  | Machines &   |  | Production   |  | Quality &    |  | Reports & |  |
|  | Employees    |  | Execution    |  | Downtime     |  | Auditing  |  |
|  +--------------+  +--------------+  +--------------+  +-----------+  |
+-----------------------------------------------------------------------+
                     |                              |
            Async SQLAlchemy 2.0                redis-py
                     |                              |
+------------------------------------+    +-----------------------------+
|        PostgreSQL 16 DB            |    |       Redis 7 Cache /       |
|    (Primary Relational Store)      |    |      PubSub Broker          |
+------------------------------------+    +-----------------------------+
```

---

## 2. Key Architectural Design Rules

1. **Domain Isolation**: Each module inside `app/modules/` owns its business logic, schemas, and service layer. Direct cross-domain database queries are discouraged; cross-domain communication occurs through service interfaces or shared events.
2. **Explicit Layering**:
   - **Router Layer** (`app/api/v1/endpoints/` or `app/modules/<domain>/router.py`): Validates HTTP requests and invokes services.
   - **Service Layer** (`app/modules/<domain>/services.py`): Encapsulates business logic and domain rules.
   - **Repository / Model Layer** (`app/modules/<domain>/models.py`): Encapsulates ORM queries and DB persistence.
   - **Schema Layer** (`app/modules/<domain>/schemas.py`): Defines Pydantic validation schemas.
3. **Async Core**: Database operations use SQLAlchemy 2.0 AsyncEngine (`asyncpg` driver) for high concurrency.
4. **No External AI Dependencies**: Core manufacturing state machines and calculation logic rely entirely on deterministic, predictable software architecture.
