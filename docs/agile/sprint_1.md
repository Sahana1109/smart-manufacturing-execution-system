# SmartMES - Sprint 1 Documentation: Authentication & RBAC Foundation

## 🎯 Sprint Goal
Implement a production-quality Authentication and Role-Based Access Control (RBAC) foundation that securely authenticates users, issues JWT tokens, enforces password hashing, and restricts protected API endpoints and UI components according to granular user roles.

---

## 📋 Sprint Backlog & User Stories

### US-AUTH-01: Secure User Login & Token Generation
- **User Story**: As a SmartMES user (operator, supervisor, or manager), I want to log in securely with my credentials so that I can access shop-floor and management features appropriate for my role.
- **Acceptance Criteria**:
  - Valid username/email and password credentials return a valid JWT access token (`Bearer`).
  - Invalid credentials return HTTP 401 Unauthenticated with a clean error message.
  - Passwords are strictly verified against bcrypt hashes.

### US-AUTH-02: User Identity & Profile Resolution (`/auth/me`)
- **User Story**: As an authenticated user, I want to retrieve my profile and assigned roles so that the UI can render my permission-aware workspace.
- **Acceptance Criteria**:
  - `GET /api/v1/auth/me` returns user identity, email, active status, and assigned roles.
  - Requests missing a valid `Bearer` header return HTTP 401.

### US-RBAC-03: Role-Based Authorization & Protected Endpoints
- **User Story**: As a system administrator, I want protected API operations restricted by user roles so that unauthorized users cannot modify user accounts or manufacturing settings.
- **Acceptance Criteria**:
  - Predefined roles supported: `ADMIN`, `PRODUCTION_MANAGER`, `SUPERVISOR`, `OPERATOR`, `QUALITY_INSPECTOR`, `INVENTORY_MANAGER`.
  - Access to role-restricted endpoints returns HTTP 403 Forbidden when the user lacks the required role.

### US-AUTH-04: User Administration & Role Assignment
- **User Story**: As an Admin, I want to create user accounts and assign roles so that shop-floor personnel can be onboarded safely.
- **Acceptance Criteria**:
  - `POST /api/v1/users` creates a new user account with duplicate username/email prevention.
  - `PUT /api/v1/users/{id}/roles` assigns roles to an existing user.

---

## ⚙️ Engineering Tasks

1. **Database Layer**: Implement SQLAlchemy `User`, `Role`, and `UserRole` models; generate Alembic migration.
2. **Security Core**: Implement bcrypt password hashing and JWT token creation/decoding.
3. **Dependencies**: Create FastAPI `get_current_user` and `require_roles` dependencies.
4. **API Endpoints**: Implement `POST /auth/login`, `GET /auth/me`, `POST /auth/logout`, and User Administration APIs under `/api/v1/users`.
5. **Seeding**: Create safe role and default admin seeding script (`app/db/seed.py`).
6. **Automated Testing**: Implement 15 comprehensive Pytest test cases in `backend/tests/test_auth.py`.
7. **Frontend Integration**: Implement Next.js Auth Context, Login page, and header identity badge with Logout.

---

## ✅ Definition of Done (DoD)

A user story or feature in Sprint 1 is complete only when:
1. Code is fully implemented adhering to Clean Architecture & SOLID principles.
2. Input validation and Pydantic schemas are enforced.
3. Password hashes are never exposed or logged.
4. Automated Pytest suite is implemented and 100% passing.
5. OpenAPI / Swagger documentation is auto-generated and verified.
6. Frontend consumes APIs correctly without duplicating business logic.
7. Security requirements (HTTP 401/403) are verified.
8. No hardcoded secrets or production passwords are committed.
9. Documentation in `docs/` is updated.
10. Feature is read
y for review on branch `feature/authentication-rbac`.
