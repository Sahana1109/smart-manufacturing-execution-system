import enum
import uuid
from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from app.modules.users.models import GUID


class ProductionPlanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ProductionPlanPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ProductionPlan(Base, TimestampMixin):
    """
    SmartMES Production Plan Entity Model
    """
    __tablename__ = "production_plans"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    plan_number = Column(String(50), unique=True, index=True, nullable=False)
    product_id = Column(GUID, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    planned_quantity = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    priority = Column(
        SQLEnum(ProductionPlanPriority, name="production_plan_priority"),
        default=ProductionPlanPriority.MEDIUM,
        nullable=False
    )
    status = Column(
        SQLEnum(ProductionPlanStatus, name="production_plan_status"),
        default=ProductionPlanStatus.DRAFT,
        nullable=False
    )
    notes = Column(Text, nullable=True)
    created_by_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="production_plans")
    created_by = relationship("User")

    def __repr__(self) -> str:
        return f"<ProductionPlan(number='{self.plan_number}', status='{self.status}', quantity={self.planned_quantity})>"
