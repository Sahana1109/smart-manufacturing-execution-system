import uuid
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from app.modules.users.models import GUID


class Product(Base, TimestampMixin):
    """
    SmartMES Product Catalog Model
    """
    __tablename__ = "products"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    product_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    unit_of_measure = Column(String(20), nullable=False, default="PCS")
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    production_plans = relationship("ProductionPlan", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Product(code='{self.product_code}', name='{self.name}', is_active={self.is_active})>"
