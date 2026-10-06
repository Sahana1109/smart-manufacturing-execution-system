import pytest
import pytest_asyncio
from datetime import date, timedelta
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
from app.modules.production_planning.models import ProductionPlan, ProductionPlanStatus, ProductionPlanPriority
from app.modules.machines.models import Machine
from app.modules.employees.models import Employee

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
        inventory_role = Role(id=6, name="INVENTORY_MANAGER", description="Inventory Manager")
        session.add_all([admin_role, manager_role, supervisor_role, operator_role, inspector_role, inventory_role])
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
async def sample_plan(db_session: AsyncSession, sample_product: Product, sample_manager: User) -> ProductionPlan:
    """
    Fixture creating an active test production plan.
    """
    plan = ProductionPlan(
        plan_number="PP-TEST-001",
        product_id=sample_product.id,
        planned_quantity=200,
        start_date=date.today(),
        due_date=date.today() + timedelta(days=7),
        priority=ProductionPlanPriority.MEDIUM,
        status=ProductionPlanStatus.PLANNED,
        created_by_id=sample_manager.id
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)
    return plan


@pytest_asyncio.fixture
async def sample_machine(db_session: AsyncSession) -> Machine:
    m = Machine(
        machine_code="TEST-MAC-01",
        name="Test CNC Mill",
        status="OPERATIONAL",
        is_active=True
    )
    db_session.add(m)
    await db_session.commit()
    await db_session.refresh(m)
    return m


@pytest_asyncio.fixture
async def sample_employee(db_session: AsyncSession) -> Employee:
    e = Employee(
        employee_code="TEST-EMP-01",
        first_name="John",
        last_name="Doe",
        role_title="CNC Operator",
        is_active=True
    )
    db_session.add(e)
    await db_session.commit()
    await db_session.refresh(e)
    return e


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
async def sample_supervisor(db_session: AsyncSession) -> User:
    supervisor_role = await db_session.get(Role, 3)
    user = User(
        email="supervisor@test.com",
        username="shop_supervisor",
        password_hash=get_password_hash("SupervisorPass123!"),
        first_name="Shop",
        last_name="Supervisor",
        is_active=True,
        roles=[supervisor_role] if supervisor_role else []
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
def supervisor_token_headers(sample_supervisor: User) -> dict:
    token = create_access_token(subject=sample_supervisor.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def operator_token_headers(sample_operator: User) -> dict:
    token = create_access_token(subject=sample_operator.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_inspector(db_session: AsyncSession) -> User:
    inspector_role = await db_session.get(Role, 5)
    user = User(
        email="inspector@test.com",
        username="quality_inspector",
        password_hash=get_password_hash("InspectorPass123!"),
        first_name="Quality",
        last_name="Inspector",
        is_active=True,
        roles=[inspector_role] if inspector_role else []
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
def inspector_token_headers(sample_inspector: User) -> dict:
    token = create_access_token(subject=sample_inspector.id)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def sample_inventory_manager(db_session: AsyncSession) -> User:
    inv_role = await db_session.get(Role, 6)
    user = User(
        email="inventory@test.com",
        username="inventory_manager",
        password_hash=get_password_hash("InventoryPass123!"),
        first_name="Inventory",
        last_name="Manager",
        is_active=True,
        roles=[inv_role] if inv_role else []
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
def inventory_manager_token_headers(sample_inventory_manager: User) -> dict:
    token = create_access_token(subject=sample_inventory_manager.id)
    return {"Authorization": f"Bearer {token}"}


