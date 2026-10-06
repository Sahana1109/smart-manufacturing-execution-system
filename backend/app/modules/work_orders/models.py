import enum
import uuid
from sqlalchemy import Column, String, Integer, Date, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from app.modules.users.models import GUID
from app.modules.production_planning.models import ProductionPlanPriority


class WorkOrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    RELEASED = "RELEASED"
    IN_PROGRESS = "IN_PROGRESS"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


# Re-use ProductionPlanPriority as WorkOrderPriority for domain consistency
WorkOrderPriority = ProductionPlanPriority


class WorkOrder(Base, TimestampMixin):
    """
    SmartMES Work Order Entity Model
    """
    __tablename__ = "work_orders"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    work_order_number = Column(String(50), unique=True, index=True, nullable=False)
    production_plan_id = Column(GUID, ForeignKey("production_plans.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id = Column(GUID, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    planned_quantity = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    priority = Column(
        SQLEnum(WorkOrderPriority, name="work_order_priority"),
        default=WorkOrderPriority.MEDIUM,
        nullable=False
    )
    status = Column(
        SQLEnum(WorkOrderStatus, name="work_order_status"),
        default=WorkOrderStatus.DRAFT,
        nullable=False
    )
    notes = Column(Text, nullable=True)
    created_by_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_machine_id = Column(GUID, ForeignKey("machines.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_employee_id = Column(GUID, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    production_plan = relationship("ProductionPlan")
    product = relationship("Product")
    created_by = relationship("User")
    assigned_machine = relationship("Machine", back_populates="work_orders")
    assigned_employee = relationship("Employee", back_populates="work_orders")

    def __repr__(self) -> str:
        return f"<WorkOrder(number='{self.work_order_number}', status='{self.status}', quantity={self.planned_quantity})>"
