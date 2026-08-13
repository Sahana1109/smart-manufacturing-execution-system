from fastapi import APIRouter
from app.core.config import settings
from app.core.database import check_db_connection
from app.core.redis import check_redis_connection

router = APIRouter()


@router.get("", summary="General System Health Check")
async def health_check():
    """
    Basic health check returning system metadata and current environment status.
    """
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "app_name": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
            "version": "0.1.0",
        },
        "message": "SmartMES backend service is online"
    }


@router.get("/db", summary="PostgreSQL Database Connection Health")
async def health_check_db():
    """
    Inspects active PostgreSQL database connection.
    """
    result = await check_db_connection()
    return {
        "success": result["connected"],
        "data": result,
        "message": "Database health check executed"
    }


@router.get("/redis", summary="Redis Cache Connection Health")
async def health_check_redis():
    """
    Inspects active Redis cache connection.
    """
    result = await check_redis_connection()
    return {
        "success": result["connected"],
        "data": result,
        "message": "Redis health check executed"
    }


@router.get("/full", summary="Comprehensive Health Check")
async def health_check_full():
    """
    Combined health check verifying app, database, and Redis.
    """
    db_result = await check_db_connection()
    redis_result = await check_redis_connection()
    
    is_healthy = db_result["connected"] and redis_result["connected"]
    
    return {
        "success": is_healthy,
        "data": {
            "overall_status": "healthy" if is_healthy else "degraded",
            "app": {
                "name": settings.PROJECT_NAME,
                "environment": settings.ENVIRONMENT,
            },
            "database": db_result,
            "redis": redis_result,
        },
        "message": "Full system health check completed"
    }
