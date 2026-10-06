import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from app.modules.users.models import GUID


class QualityStatus(str, enum.Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    REWORK_REQUIRED = "REWORK_REQUIRED"


class DefectType(str, enum.Enum):
    DIMENSIONAL = "DIMENSIONAL"
    SURFACE = "SURFACE"
    MATERIAL = "MATERIAL"
    ASSEMBLY = "ASSEMBLY"
    FUNCTIONAL = "FUNCTIONAL"
    COSMETIC = "COSMETIC"
    OTHER = "OTHER"


class DefectSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class QualityInspection(Base, TimestampMixin):
    """
    SmartMES Quality Inspection Model
    """
    __tablename__ = "quality_inspections"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    work_order_id = Column(GUID, ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    inspector_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    inspected_quantity = Column(Integer, nullable=False, default=0)
    accepted_quantity = Column(Integer, nullable=False, default=0)
    rejected_quantity = Column(Integer, nullable=False, default=0)
    status = Column(
        SQLEnum(QualityStatus, name="quality_status"),
        default=QualityStatus.PENDING,
        nullable=False
    )
    remarks = Column(Text, nullable=True)
    inspection_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    work_order = relationship("WorkOrder", back_populates="inspections")
    inspector = relationship("User")
    defects = relationship("QualityDefect", back_populates="inspection", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<QualityInspection(wo_id='{self.work_order_id}', status='{self.status}', inspected={self.inspected_quantity})>"


class QualityDefect(Base, TimestampMixin):
    """
    SmartMES Quality Defect Model
    """
    __tablename__ = "quality_defects"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    inspection_id = Column(GUID, ForeignKey("quality_inspections.id", ondelete="CASCADE"), nullable=False, index=True)
    defect_type = Column(
        SQLEnum(DefectType, name="defect_type"),
        default=DefectType.OTHER,
        nullable=False
    )
    severity = Column(
        SQLEnum(DefectSeverity, name="defect_severity"),
        default=DefectSeverity.MEDIUM,
        nullable=False
    )
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    remarks = Column(Text, nullable=True)

    # Relationships
    inspection = relationship("QualityInspection", back_populates="defects")

    def __repr__(self) -> str:
        return f"<QualityDefect(type='{self.defect_type}', severity='{self.severity}', qty={self.quantity})>"
