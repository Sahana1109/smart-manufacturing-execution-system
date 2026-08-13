# SmartMES - REST API Conventions & Standard Rules

## 1. OpenAPI Standards
All endpoints are exposed under `/api/v1/` and automatically documented via FastAPI OpenAPI specification (`/docs` and `/redoc`).

---

## 2. Standard URL Patterns

| Action | HTTP Method | Path Pattern | Example Path |
| :--- | :--- | :--- | :--- |
| **List Resource** | `GET` | `/api/v1/{resources}` | `/api/v1/work-orders` |
| **Get Single** | `GET` | `/api/v1/{resources}/{id}` | `/api/v1/work-orders/{id}` |
| **Create Resource** | `POST` | `/api/v1/{resources}` | `/api/v1/work-orders` |
| **Update Resource** | `PUT` | `/api/v1/{resources}/{id}` | `/api/v1/work-orders/{id}` |
| **Partial Update** | `PATCH` | `/api/v1/{resources}/{id}` | `/api/v1/work-orders/{id}` |
| **Delete Resource** | `DELETE` | `/api/v1/{resources}/{id}` | `/api/v1/work-orders/{id}` |

---

## 3. Standard API Response Structure

All responses follow a predictable JSON payload format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Resource processed successfully",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Work Order with ID '123' does not exist",
    "details": []
  }
}
```
