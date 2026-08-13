# SmartMES - Software Requirements Specification (SRS)

## 1. Document Overview
This document specifies the functional and non-functional requirements for **SmartMES** (Smart Manufacturing Execution & Work Order Management System).

---

## 2. Functional Requirements by Module

### FR-01: Authentication & User Management
- **FR-01.1**: The system shall allow users to log in securely using username/email and password credentials.
- **FR-01.2**: The system shall issue JSON Web Tokens (JWT) upon successful authentication.
- **FR-01.3**: The system shall enforce Role-Based Access Control (RBAC) across all API endpoints and frontend views.

### FR-02: Master Data Management
- **FR-02.1**: The system shall maintain product catalogs, part numbers, SKUs, and unit of measures.
- **FR-02.2**: The system shall store multi-level Bill of Materials (BOM) definitions specifying required raw materials per product.
- **FR-02.3**: The system shall maintain supplier references, machine registries, and employee operator skill matrices.

### FR-03: Inventory & Warehouse Management
- **FR-03.1**: The system shall track inventory stock levels across multiple warehouses, zones, racks, and bins.
- **FR-03.2**: The system shall record raw material allocations and finished goods receipts with lot/batch tracking.

### FR-04: Production Planning & Work Orders
- **FR-04.1**: The system shall support creation and scheduling of Production Plans and Work Orders.
- **FR-04.2**: Work Orders shall specify target quantities, bill of materials, routing steps, assigned machines, and target start/completion times.
- **FR-04.3**: The system shall enforce Work Order state transitions (Draft -> Released -> In Progress -> Paused -> Completed -> Closed).

### FR-05: Shop Floor Production Execution
- **FR-05.1**: Shop floor operators shall be able to start, pause, resume, and complete work order operations.
- **FR-05.2**: The system shall log real-time production counts (good parts, scrap parts) per machine shift.

### FR-06: Quality Inspection & Assurance
- **FR-06.1**: Quality inspectors shall be able to execute QA checklists for first-piece, in-process, and final production inspections.
- **FR-06.2**: The system shall log defect codes, scrap quantities, and pass/fail disposition.

### FR-07: Downtime & OEE Tracking
- **FR-07.1**: The system shall capture machine downtime events with categorized reason codes (e.g., Mechanical Failure, Tool Change, Material Shortage).
- **FR-07.2**: The system shall compute operational uptime and provide foundation data for Overall Equipment Effectiveness (OEE).

### FR-08: Reporting & Analytics
- **FR-08.1**: The system shall generate operational summaries including production yield, scrap rate, machine utilization, and order execution status.

### FR-09: Barcode / QR Code Management
- **FR-09.1**: The system shall generate unique QR codes and barcodes for work orders, batches, machines, and inventory locations.

---

## 3. Non-Functional Requirements

### NFR-01: Performance & Scalability
- **NFR-01.1**: API responses for standard queries shall execute under 200ms at 95th percentile.
- **NFR-01.2**: Architecture must support concurrent shop-floor requests without locking database resources.

### NFR-02: Security
- **NFR-02.1**: Passwords must be hashed using argon2 or bcrypt with strong salt.
- **NFR-02.2**: All endpoints except public health check must require valid JWT authorization header.
- **NFR-02.3**: Sensitive actions must produce immutable Audit Log entries.

### NFR-03: Maintainability & Code Quality
- **NFR-03.1**: System must be implemented as a Modular Monolith with clear boundary encapsulation.
- **NFR-03.2**: 100% of Python backend code must include type hints and pass strict Pydantic validation.
- **NFR-03.3**: Frontend code must be strictly typed using TypeScript.
