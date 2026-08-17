import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user, require_roles
from app.modules.products import service as product_service
from app.modules.products.schemas import ProductCreate, ProductResponse

router = APIRouter()


@router.get(
    "",
    response_model=List[ProductResponse],
    summary="List all catalog products"
)
async def get_products(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Returns product catalog items. Accessible to all authenticated users.
    """
    return await product_service.list_products(db, active_only=active_only)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new catalog product (Admin / Production Manager)",
    dependencies=[Depends(require_roles("ADMIN", "PRODUCTION_MANAGER"))]
)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new product item. Requires ADMIN or PRODUCTION_MANAGER role.
    """
    return await product_service.create_product(db, product_in)
