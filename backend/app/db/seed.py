import os
import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.modules.roles.models import Role
from app.modules.users.models import User
from app.modules.products.models import Product

logger = logging.getLogger(__name__)

INITIAL_ROLES = [
    {"name": "ADMIN", "description": "Full system administrator with unrestricted access"},
    {"name": "PRODUCTION_MANAGER", "description": "Production planning, scheduling, and work order management"},
    {"name": "SUPERVISOR", "description": "Shop-floor team supervisor and machine allocation"},
    {"name": "OPERATOR", "description": "Machine and work order execution operator"},
    {"name": "QUALITY_INSPECTOR", "description": "Quality assurance checklist and defect inspector"},
    {"name": "INVENTORY_MANAGER", "description": "Stock movement, warehouse, and lot/batch manager"},
]

INITIAL_PRODUCTS = [
    {"product_code": "PRD-STEEL-001", "name": "Precision Steel Housing 50mm", "description": "High-grade alloy steel housing enclosure", "unit_of_measure": "PCS"},
    {"product_code": "PRD-ALUM-002", "name": "Aluminum Heat Sink Plate 120mm", "description": "Extruded aluminum heat sink element", "unit_of_measure": "PCS"},
    {"product_code": "PRD-GEAR-003", "name": "Heavy Duty Spur Gear Assembly", "description": "Hardened steel transmission gear assembly", "unit_of_measure": "SETS"},
]


async def seed_db(db: AsyncSession) -> None:
    """
    Seeds initial default roles, sample products, and a development administrator account.
    """
    # 1. Seed Roles
    logger.info("Checking initial roles...")
    for role_data in INITIAL_ROLES:
        stmt = select(Role).where(Role.name == role_data["name"])
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()
        if not existing:
            logger.info(f"Seeding role: {role_data['name']}")
            role = Role(name=role_data["name"], description=role_data["description"])
            db.add(role)
    await db.commit()

    # 2. Seed Sample Products
    logger.info("Checking initial sample products...")
    for prod_data in INITIAL_PRODUCTS:
        stmt = select(Product).where(Product.product_code == prod_data["product_code"])
        res = await db.execute(stmt)
        existing_prod = res.scalar_one_or_none()
        if not existing_prod:
            logger.info(f"Seeding product: {prod_data['product_code']}")
            prod = Product(
                product_code=prod_data["product_code"],
                name=prod_data["name"],
                description=prod_data["description"],
                unit_of_measure=prod_data["unit_of_measure"],
                is_active=True
            )
            db.add(prod)
    await db.commit()

    # 3. Seed Admin User
    admin_email = os.getenv("INITIAL_ADMIN_EMAIL", "admin@smartmes.local")
    admin_username = os.getenv("INITIAL_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("INITIAL_ADMIN_PASSWORD", "SmartMES_DevAdminPass_2026!")

    stmt = select(User).where(User.username == admin_username)
    res = await db.execute(stmt)
    existing_admin = res.scalar_one_or_none()

    if not existing_admin:
        logger.info(f"Seeding development admin user: {admin_username} ({admin_email})")
        hashed_pwd = get_password_hash(admin_password)
        
        admin_role_stmt = select(Role).where(Role.name == "ADMIN")
        admin_role_res = await db.execute(admin_role_stmt)
        admin_role = admin_role_res.scalar_one()

        admin_user = User(
            email=admin_email,
            username=admin_username,
            password_hash=hashed_pwd,
            first_name="System",
            last_name="Administrator",
            is_active=True,
            roles=[admin_role]
        )
        db.add(admin_user)
        await db.commit()
        logger.info("Admin user seeded successfully.")
    else:
        logger.info("Development admin user already exists.")


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await seed_db(session)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
