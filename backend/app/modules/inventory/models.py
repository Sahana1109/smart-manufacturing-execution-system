import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from app.modules.users.models import GUID


class MaterialUnit(str, enum.Enum):
    PCS = "PCS"
    KG = "KG"
    L = "L"
    M = "M"
    OTHER = "OTHER"


class MovementType(str, enum.Enum):
    RECEIPT = "RECEIPT"
    RESERVATION = "RESERVATION"
    RELEASE = "RELEASE"
    CONSUMPTION = "CONSUMPTION"
    ADJUSTMENT = "ADJUSTMENT"


class Material(Base, TimestampMixin):
    """
    SmartMES Material Item Master Entity Model
    """
    __tablename__ = "materials"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    material_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(
        SQLEnum(MaterialUnit, name="material_unit"),
        default=MaterialUnit.PCS,
        nullable=False
    )
    reorder_level = Column(Integer, nullable=False, default=10)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    stock = relationship("InventoryStock", back_populates="material", uselist=False, cascade="all, delete-orphan")
    movements = relationship("StockMovement", back_populates="material", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Material(code='{self.material_code}', name='{self.name}', unit='{self.unit}')>"


class InventoryStock(Base, TimestampMixin):
    """
    SmartMES Inventory Stock Level Entity Model
    """
    __tablename__ = "inventory_stocks"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    material_id = Column(GUID, ForeignKey("materials.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    location = Column(String(100), nullable=False, default="MAIN-WAREHOUSE")

    # Relationships
    material = relationship("Material", back_populates="stock")

    @property
    def available_quantity(self) -> int:
        return max(0, (self.quantity or 0) - (self.reserved_quantity or 0))

    def __repr__(self) -> str:
        return f"<InventoryStock(mat_id='{self.material_id}', qty={self.quantity}, reserved={self.reserved_quantity}, avail={self.available_quantity})>"


class StockMovement(Base, TimestampMixin):
    """
    SmartMES Stock Movement Audit Entity Model
    """
    __tablename__ = "stock_movements"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    material_id = Column(GUID, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True)
    work_order_id = Column(GUID, ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, index=True)
    movement_type = Column(
        SQLEnum(MovementType, name="movement_type"),
        nullable=False
    )
    quantity = Column(Integer, nullable=False)
    reference = Column(Text, nullable=True)
    performed_by_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    material = relationship("Material", back_populates="movements")
    work_order = relationship("WorkOrder")
    performed_by = relationship("User")

    def __repr__(self) -> str:
        return f"<StockMovement(type='{self.movement_type}', qty={self.quantity}, mat_id='{self.material_id}')>"
