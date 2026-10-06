from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.modules.authentication import router as auth_router
from app.modules.users import router as users_router
from app.modules.products import router as products_router
from app.modules.production_planning import router as plans_router
from app.modules.machines import router as machines_router
from app.modules.employees import router as employees_router
from app.modules.work_orders import router as work_orders_router
from app.modules.quality import router as quality_router

api_router = APIRouter()

# Core System Diagnostics
api_router.include_router(health.router, prefix="/health", tags=["Health & Diagnostics"])

# Authentication & Identity
api_router.include_router(auth_router.router, prefix="/auth", tags=["Authentication & Security"])

# User Administration & RBAC
api_router.include_router(users_router.router, prefix="/users", tags=["User Management & Roles"])

# Master Data - Products, Machines, Employees
api_router.include_router(products_router.router, prefix="/products", tags=["Products Catalog"])
api_router.include_router(machines_router.router, prefix="/machines", tags=["Machines Catalog"])
api_router.include_router(employees_router.router, prefix="/employees", tags=["Employees Catalog"])

# Production Planning & Work Orders
api_router.include_router(plans_router.router, prefix="/production-plans", tags=["Production Planning"])
api_router.include_router(work_orders_router.router, prefix="/work-orders", tags=["Work Order Management"])

# Quality Inspection & Control
api_router.include_router(quality_router.router, prefix="/quality", tags=["Quality Inspection & Control"])

