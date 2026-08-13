import logging
from typing import Optional
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """
    Returns an active async Redis client instance.
    """
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis_client() -> None:
    """
    Closes the Redis client connection pool gracefully.
    """
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None


async def check_redis_connection() -> dict:
    """
    Utility function to verify Redis connection health.
    Returns status dict without crashing if connection fails.
    """
    try:
        client = await get_redis_client()
        pong = await client.ping()
        if pong:
            return {"status": "healthy", "connected": True, "details": "Redis ping successful"}
    except Exception as e:
        logger.warning(f"Redis connection check failed: {str(e)}")
        return {"status": "unhealthy", "connected": False, "details": str(e)}
    return {"status": "unhealthy", "connected": False, "details": "Redis ping failed"}
