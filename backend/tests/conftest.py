import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.core.database import get_db
from app.core.security import get_password_hash, create_access_token
from app.modules.users.models import User
from app.modules.roles.models import Role

# In-memory SQLite async database engine for isolated Pytest execution
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates clean database schema for each test function and yields async session.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        # Seed test roles
        admin_role = Role(name="ADMIN", description="Administrator")
        operator_role = Role(name="OPERATOR", description="Shop-Floor Operator")
        session.add_all([admin_role, operator_role])
        await session.commit()

        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    AsyncClient fixture overriding get_db dependency with test database session.
    """
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_admin(db_session: AsyncSession) -> User:
    """
    Fixture creating an active Admin user.
    """
    admin_role_res = await db_session.execute(
        Role.__table__.select().where(Role.name == "ADMIN")
    )
    # Fetch role instance
    admin_role = (await db_session.get(Role, 1))

    user = User(
        email="admin@test.com",
        username="admin_user",
        password_hash=get_password_hash("AdminPass123!"),
        first_name="Admin",
        last_name="Test",
        is_active=True,
        roles=[admin_role] if admin_role else []
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_operator(db_session: AsyncSession) -> User:
    """
    Fixture creating an active Operator user.
    """
    operator_role = (await db_session.get(Role, 2))

    user = User(
        email="operator@test.com",
        username="operator_user",
        password_hash=get_password_hash("OperatorPass123!"),
        first_name="Operator",
        last_name="Test",
        is_active=True,
        roles=[operator_role] if operator_role else []
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
def admin_token_headers(sample_admin: User) -> dict:
    """
    Returns Authorization Bearer header dict for Admin user.
    """
    token = create_access_token(subject=sample_admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def operator_token_headers(sample_operator: User) -> dict:
    """
    Returns Authorization Bearer header dict for Operator user.
    """
    token = create_access_token(subject=sample_operator.id)
    return {"Authorization": f"Bearer {token}"}
