from typing import AsyncGenerator
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for yielding async SQLAlchemy database sessions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def check_db_connection() -> dict:
    """
    Utility function to verify database connectivity.
    Returns status dict without crashing if connection fails.
    """
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                return {"status": "healthy", "connected": True, "details": "PostgreSQL connection verified"}
    except Exception as e:
        logger.warning(f"Database connection check failed: {str(e)}")
        return {"status": "unhealthy", "connected": False, "details": str(e)}
    return {"status": "unhealthy", "connected": False, "details": "Unknown DB response"}
