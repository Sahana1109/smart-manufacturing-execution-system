# SMARTMES: Smart Manufacturing Execution & Work Order Management System

SmartMES is an enterprise-oriented, production-ready Manufacturing Execution System designed to digitally orchestrate and monitor the complete manufacturing lifecycle—from production planning and work order execution to inventory tracking, quality control, machine state management, downtime reporting, barcode identification, and executive reporting dashboards.

---

## 🎯 Project Vision & Goals

SmartMES bridges the gap between enterprise resource planning (ERP) and shop-floor machinery execution. It delivers real-time visibility into production efficiency, quality assurance, downtime analytics, and material flows while maintaining strict traceability and security.

### Core Objectives & Principles
1. **Software Engineering Excellence**: Adheres to SOLID principles, DRY, KISS, low coupling, high cohesion, and Clean Architecture principles.
2. **Modular Monolith Backend**: Domain-driven modular structure for high maintainability, allowing easy future separation into microservices if needed without premature complexity.
3. **Enterprise Security & Auditability**: Full Role-Based Access Control (RBAC), JWT authentication, and comprehensive action auditing.
4. **Cloud-Ready & Vendor-Independent**: Completely runnable locally via Docker Compose without relying on proprietary cloud services or paid subscriptions.
5. **Deterministic Core Architecture**: Built strictly on robust software design without external AI dependencies or non-deterministic LLMs.

---

## 🚀 Sprints 1–8 Completed Modules Summary

* **Sprint 1 — Authentication & RBAC**: JWT authentication, bcrypt password hashing, 6 granular system roles (`ADMIN`, `PRODUCTION_MANAGER`, `SUPERVISOR`, `QUALITY_INSPECTOR`, `INVENTORY_MANAGER`, `OPERATOR`), protected endpoint decorators.
* **Sprint 2 — Production Planning**: Product SKU catalog management, multi-priority production planning (`LOW`, `MEDIUM`, `HIGH`, `URGENT`), target quantity tracking, plan status transitions (`DRAFT`, `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`).
* **Sprint 3 — Work Order Management**: Work order lifecycle (`DRAFT` → `RELEASED` → `IN_PROGRESS` ↔ `PAUSED` → `COMPLETED` → `CLOSED`/`CANCELLED`), plan linkage, quantity validations, priority routing.
* **Sprint 4 — Machine & Operator Assignment**: Machine master catalog (`OPERATIONAL`, `IN_USE`, `MAINTENANCE`, `INACTIVE`), operator/employee profiles, machine & operator assignment to work orders, assignment validation rules.
* **Sprint 5 — Shop Floor Production Execution**: Production execution state machine, start/pause/resume/complete APIs, actual timestamps, produced quantity tracking, machine status auto-synchronization (`IN_USE` / `OPERATIONAL`), shop-floor downtime logging.
* **Sprint 6 — Quality Inspection & Control**: Quality inspection module (`PENDING`, `PASSED`, `FAILED`, `REWORK_REQUIRED`), defect categorizations (`DIMENSIONAL`, `SURFACE`, `MATERIAL`, `ASSEMBLY`, `FUNCTIONAL`, `COSMETIC`, `OTHER`), severity levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), accepted vs rejected quantity tracking, quality dashboard.
* **Sprint 7 — Inventory & Material Tracking**: Material master catalog, practical units (`PCS`, `KG`, `L`, `M`, `OTHER`), stock level tracking (`quantity`, `reserved_quantity`, `available_quantity`), stock movement audit trail (`RECEIPT`, `RESERVATION`, `RELEASE`, `CONSUMPTION`, `ADJUSTMENT`), work order allocation/consumption, low-stock detection (`available_quantity <= reorder_level`), `/inventory` dashboard.
* **Sprint 8 — Reports & Management Dashboards**: Executive management dashboard (`/dashboard`), 5-row KPI breakdown, Production report, Quality report, Inventory report, Machine report, Operator summary, date range filtering (`from_date`, `to_date`), CSV export capability (`.csv`).

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Next.js 14+ (App Router), React 18+, TypeScript | Modern, high-performance web interface |
| **Styling** | Tailwind CSS, Lucide Icons, Custom Glassmorphism CSS | Clean, high-density industrial dashboard design |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2 | High-concurrency, type-safe REST API framework |
| **Database** | PostgreSQL 16 | Primary relational storage with ACID compliance |
| **ORM & Migrations** | SQLAlchemy 2.0 (Async), Alembic | Async database operations and schema migration control |
| **Caching & Messaging**| Redis 7 | High-speed cache and pub/sub message broker foundation |
| **Containerization** | Docker, Docker Compose | Multi-container local execution environment |
| **Testing** | Pytest (106 unit & integration tests) | Automated test suite with 100% pass rate |
| **API Spec** | OpenAPI / Swagger | Self-documenting interactive API standard at `/docs` |

---

## 📁 Repository Structure

```
smartmes/
├── frontend/             # Next.js App Router (TS, Tailwind CSS)
│   ├── app/              # App Router Pages (/dashboard, /inventory, /work-orders, etc.)
│   ├── components/       # UI Components (Modals, Nav, Cards, Layouts)
│   ├── lib/              # API Client & Auth Context
│   └── types/            # TypeScript interfaces
├── backend/              # FastAPI modular backend application
│   ├── app/
│   │   ├── api/          # Global API router and versioned endpoints (/api/v1)
│   │   ├── core/         # Settings, security, database & redis connections
│   │   ├── db/           # Session setup and base model declarative classes
│   │   └── modules/      # Domain modules (auth, work_orders, quality, inventory, reports, etc.)
│   ├── alembic/          # Database migration environment (001 through 006)
│   └── tests/            # Pytest suite (106 unit, integration, and E2E tests)
├── database/             # Database initialization scripts and schemas
├── docs/                 # Architectural specifications, API docs, and sprint plans
│   ├── agile/            # Sprint documentation (sprint_1 through sprint_8, final_integration)
├── docker/               # Container files (Dockerfile.backend, Dockerfile.frontend)
├── scripts/              # Developer helper scripts (setup, start, migrate, seed)
├── .env.example          # Template for local environment variables
├── .gitignore            # Git exclusion rules
├── docker-compose.yml    # Multi-container service definition
└── README.md             # Project overview & quickstart
```

---

## 🚀 Quick Start Guide

### Prerequisites
- [Node.js](https://nodejs.org/) v18+ and `npm`
- [Python](https://www.python.org/) 3.11+
- [Docker](https://www.docker.com/) & Docker Compose (optional for containerized run)
- [PostgreSQL](https://www.postgresql.org/) 16+ & [Redis](https://redis.io/) 7+ (if running locally without Docker)

### Option A: Running with Docker Compose (Recommended)

```bash
# 1. Clone the repository and navigate to smartmes
cd smartmes

# 2. Copy environment template
cp .env.example .env

# 3. Build and launch all services (Frontend, Backend, PostgreSQL, Redis)
docker-compose up --build -d

# 4. Access services:
# Frontend App:     http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
# API Healthcheck:  http://localhost:8000/api/v1/health
```

### Option B: Local Manual Development Setup

#### 1. Backend Setup
```bash
cd smartmes/backend

# Create virtual environment
python -m venv venv
# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# Activate virtual environment (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Run FastAPI server with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. Frontend Setup
```bash
cd smartmes/frontend

# Install dependencies
npm install

# Run Next.js development server
npm run dev

# Or build for production
npm run build
```

---

## 🧪 Testing

```bash
# Run complete backend test suite (106 tests across Sprints 1–8 & E2E Integration)
cd smartmes/backend
pytest

# Run Next.js frontend production build verification
cd smartmes/frontend
npm run build
```

---

## 📄 License
Internal SmartMES Development Project - All Rights Reserved.

