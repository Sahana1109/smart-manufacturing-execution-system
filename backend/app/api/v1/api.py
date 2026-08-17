from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.modules.authentication import router as auth_router
from app.modules.users import router as users_router
from app.modules.products import router as products_router
from app.modules.production_planning import router as plans_router

api_router = APIRouter()

# Core System Diagnostics
api_router.include_router(health.router, prefix="/health", tags=["Health & Diagnostics"])

# Authentication & Identity
api_router.include_router(auth_router.router, prefix="/auth", tags=["Authentication & Security"])

# User Administration & RBAC
api_router.include_router(users_router.router, prefix="/users", tags=["User Management & Roles"])

# Master Data - Products
api_router.include_router(products_router.router, prefix="/products", tags=["Products Catalog"])

# Production Planning
api_router.include_router(plans_router.router, prefix="/production-plans", tags=["Production Planning"])
