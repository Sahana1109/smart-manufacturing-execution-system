import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Date, DateTime, Text, ForeignKey, Enum as SQLEnum
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
    produced_quantity = Column(Integer, nullable=False, default=0)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    actual_start_time = Column(DateTime(timezone=True), nullable=True)
    actual_completion_time = Column(DateTime(timezone=True), nullable=True)
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
    downtime_records = relationship("DowntimeRecord", back_populates="work_order", cascade="all, delete-orphan")
    inspections = relationship("QualityInspection", back_populates="work_order", cascade="all, delete-orphan", order_by="desc(QualityInspection.created_at)")

    @property
    def remaining_quantity(self) -> int:
        return max(0, self.planned_quantity - (self.produced_quantity or 0))

    @property
    def progress_percentage(self) -> float:
        if not self.planned_quantity or self.planned_quantity <= 0:
            return 0.0
        return round(min(100.0, ((self.produced_quantity or 0) / self.planned_quantity) * 100.0), 1)

    @property
    def quality_status(self) -> str:
        if "inspections" in self.__dict__ and self.inspections:
            latest = self.inspections[0]
            status_val = latest.status
            return status_val.value if hasattr(status_val, 'value') else str(status_val)
        return "PENDING"

    def __repr__(self) -> str:
        return f"<WorkOrder(number='{self.work_order_number}', status='{self.status}', planned={self.planned_quantity}, produced={self.produced_quantity})>"


class DowntimeRecord(Base, TimestampMixin):
    """
    SmartMES Shop Floor Downtime / Delay Record Entity Model
    """
    __tablename__ = "downtime_records"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    work_order_id = Column(GUID, ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    machine_id = Column(GUID, ForeignKey("machines.id", ondelete="SET NULL"), nullable=True, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    reason = Column(String(100), nullable=False)  # e.g. MACHINE_BREAKDOWN, MATERIAL_UNAVAILABLE, OPERATOR_UNAVAILABLE, MAINTENANCE, POWER_FAILURE, OTHER
    remarks = Column(Text, nullable=True)
    recorded_by_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    work_order = relationship("WorkOrder", back_populates="downtime_records")
    machine = relationship("Machine")
    recorded_by = relationship("User")

    def __repr__(self) -> str:
        return f"<DowntimeRecord(wo_id='{self.work_order_id}', reason='{self.reason}', minutes={self.duration_minutes})>"
