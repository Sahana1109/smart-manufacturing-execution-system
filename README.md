# SMARTMES: Smart Manufacturing Execution & Work Order Management System

SmartMES is an enterprise-oriented, production-ready Manufacturing Execution System designed to digitally orchestrate and monitor the complete manufacturing lifecycle—from production planning and work order execution to inventory tracking, quality control, machine state management, downtime reporting, and barcode identification.

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

## 🛠️ Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Next.js 14+ (App Router), React 18+, TypeScript | Modern, high-performance web interface |
| **Styling** | Tailwind CSS, Lucide Icons, Custom CSS System | Clean, high-density industrial dashboard design |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2 | High-concurrency, type-safe REST API framework |
| **Database** | PostgreSQL 16 | Primary relational storage with ACID compliance |
| **ORM & Migrations** | SQLAlchemy 2.0 (Async), Alembic | Async database operations and schema migration control |
| **Caching & Messaging**| Redis 7 | High-speed cache and pub/sub message broker foundation |
| **Containerization** | Docker, Docker Compose | Multi-container local execution environment |
| **Testing** | Pytest (Backend), Playwright (Frontend E2E) | Automated unit, integration, and end-to-end testing |
| **API Spec** | OpenAPI / Swagger | Self-documenting interactive API standard |

---

## 📁 Repository Structure

```
smartmes/
├── frontend/             # Next.js App Router (TS, Tailwind CSS)
├── backend/              # FastAPI modular backend application
│   ├── app/
│   │   ├── api/          # Global API router and versioned endpoints
│   │   ├── core/         # Settings, security, database & redis connections
│   │   ├── db/           # Session setup and base model declarative classes
│   │   └── modules/      # 18 Domain-driven modules (auth, work_orders, etc.)
│   ├── alembic/          # Database migration environment
│   └── tests/            # Pytest suite (unit & integration tests)
├── database/             # Database initialization scripts and schemas
├── tests/                # E2E integration test suite (Playwright framework)
├── docs/                 # Architectural specifications, API docs, and sprint plans
│   ├── requirements/     # SRS (Functional and non-functional requirements)
│   ├── architecture/     # System architecture and domain boundary specs
│   ├── database/         # Data model and migration guidelines
│   ├── api/              # API standard practices
│   ├── testing/          # QA and testing strategy
│   ├── agile/            # Sprint roadmap and phase definitions
│   └── deployment/       # Docker and local deployment guide
├── docker/               # Container files (Dockerfile.backend, Dockerfile.frontend)
├── scripts/              # Developer helper scripts (setup, start, migrate, seed)
├── .github/              # CI/CD GitHub Actions workflows
├── .env.example          # Template for local environment variables
├── .gitignore            # Git exclusion rules
├── docker-compose.yml    # Multi-container service definition
└── README.md             # Project overview & quickstart
```

---

## 🧩 Domain Modules Architecture

Backend and Frontend architectures are organized into 18 domain-focused modules:

1. **Authentication**: JWT token management, login/logout, password hashing.
2. **Users**: User accounts, profile management, status tracking.
3. **Roles & Permissions**: Fine-grained Role-Based Access Control (RBAC).
4. **Products**: Finished goods, raw materials, part catalogs, SKUs.
5. **Bill of Materials (BOM)**: Multi-level BOM structures, component quantities.
6. **Suppliers**: Vendor catalogs, lead times, purchasing references.
7. **Inventory**: Stock levels, stock movements, lot/batch tracking.
8. **Warehouses**: Warehouse locations, bins, racks, zone management.
9. **Machines**: Work center registration, machine status, operational capacity.
10. **Employees**: Operator profiles, shift schedules, skill certifications.
11. **Production Planning**: Production orders, target quantities, schedules.
12. **Work Orders**: Dispatching, job routing, status state machines.
13. **Production Execution**: Operator task execution, output logging, cycle times.
14. **Quality Inspection**: QA checklists, defect logging, scrap reporting, pass/fail status.
15. **Downtime**: Machine stoppage reasons, downtime logs, OEE metrics support.
16. **Reports**: Production performance, yield analytics, summary reports.
17. **Notifications**: System alerts, machine status change notifications.
18. **Audit Logs**: Immutable event logs for compliance and security auditing.

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
```

---

## 🧪 Testing

```bash
# Backend unit & integration tests
cd smartmes/backend
pytest

# Frontend E2E tests
cd smartmes/tests
npx playwright test
```

---

## 📄 License
Internal SmartMES Development Project - All Rights Reserved.
