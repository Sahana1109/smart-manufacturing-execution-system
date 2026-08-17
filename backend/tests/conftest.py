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
from app.modules.products.models import Product

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
        admin_role = Role(id=1, name="ADMIN", description="Administrator")
        manager_role = Role(id=2, name="PRODUCTION_MANAGER", description="Production Manager")
        supervisor_role = Role(id=3, name="SUPERVISOR", description="Supervisor")
        operator_role = Role(id=4, name="OPERATOR", description="Shop-Floor Operator")
        inspector_role = Role(id=5, name="QUALITY_INSPECTOR", description="Quality Inspector")
        session.add_all([admin_role, manager_role, supervisor_role, operator_role, inspector_role])
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
async def sample_product(db_session: AsyncSession) -> Product:
    """
    Fixture creating an active test product.
    """
    prod = Product(
        product_code="TEST-PRD-001",
        name="Test Gear Assembly",
        description="Active test product",
        unit_of_measure="PCS",
        is_active=True
    )
    db_session.add(prod)
    await db_session.commit()
    await db_session.refresh(prod)
    return prod


@pytest_asyncio.fixture
async def sample_admin(db_session: AsyncSession) -> User:
    admin_role = await db_session.get(Role, 1)
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
async def sample_manager(db_session: AsyncSession) -> User:
    manager_role = await db_session.get(Role, 2)
    user = User(
        email="manager@test.com",
        username="prod_manager",
        password_hash=get_password_hash("ManagerPass123!"),
        first_name="Production",
        last_name="Manager",
        is_active=True,
        roles=[manager_role] if manager_role else []
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_operator(db_session: AsyncSession) -> User:
    operator_role = await db_session.get(Role, 4)
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
    token = create_access_token(subject=sample_admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def manager_token_headers(sample_manager: User) -> dict:
    token = create_access_token(subject=sample_manager.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def operator_token_headers(sample_operator: User) -> dict:
    token = create_access_token(subject=sample_operator.id)
    return {"Authorization": f"Bearer {token}"}
