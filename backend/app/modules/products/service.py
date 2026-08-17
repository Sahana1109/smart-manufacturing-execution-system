import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.modules.products.models import Product
from app.modules.products.schemas import ProductCreate


async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
    """
    Creates a new product catalog item after checking uniqueness of product_code.
    """
    stmt = select(Product).where(Product.product_code == product_in.product_code)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with code '{product_in.product_code}' already exists"
        )

    product = Product(
        product_code=product_in.product_code,
        name=product_in.name,
        description=product_in.description,
        unit_of_measure=product_in.unit_of_measure,
        is_active=product_in.is_active,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def list_products(db: AsyncSession, active_only: bool = False) -> List[Product]:
    """
    Lists product catalog items.
    """
    stmt = select(Product)
    if active_only:
        stmt = stmt.where(Product.is_active.is_(True))
    stmt = stmt.order_by(Product.product_code.asc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_product_by_id(db: AsyncSession, product_id: uuid.UUID) -> Optional[Product]:
    """
    Retrieves product by UUID.
    """
    stmt = select(Product).where(Product.id == product_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()
