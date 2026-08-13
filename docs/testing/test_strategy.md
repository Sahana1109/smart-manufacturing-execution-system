# SmartMES - Testing Strategy

## 1. Test Architecture

SmartMES enforces high quality standards across all software layers:

```
                  / \
                 /   \  E2E Tests (Playwright)
                /-----\
               /       \  Integration Tests (FastAPI TestClient + Postgres)
              /---------\
             /           \  Unit Tests (Pytest + Pydantic + Mocks)
            +-------------+
```

---

## 2. Test Suites

### Backend Unit & Integration Tests
- **Location**: `backend/tests/`
- **Framework**: `pytest`, `pytest-asyncio`, `httpx`
- **Scope**: API endpoint responses, service business rules, database connection pooling, state machine transitions.

### Frontend E2E Tests
- **Location**: `tests/e2e/`
- **Framework**: `playwright`
- **Scope**: User authentication flows, work order execution screens, shop-floor tablet interface responses.
