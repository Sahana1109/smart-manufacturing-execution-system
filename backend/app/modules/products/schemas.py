import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    product_code: str = Field(..., min_length=2, max_length=50, description="Unique SKU / Product Code")
    name: str = Field(..., min_length=2, max_length=255, description="Product display name")
    description: Optional[str] = None
    unit_of_measure: str = Field(default="PCS", min_length=1, max_length=20)
    is_active: bool = True


class ProductResponse(BaseModel):
    id: uuid.UUID
    product_code: str
    name: str
    description: Optional[str] = None
    unit_of_measure: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
