import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from app.modules.users.models import GUID


class Machine(Base, TimestampMixin):
    """
    SmartMES Machine Entity Model
    """
    __tablename__ = "machines"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    machine_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="OPERATIONAL")
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    work_orders = relationship("WorkOrder", back_populates="assigned_machine")

    def __repr__(self) -> str:
        return f"<Machine(code='{self.machine_code}', name='{self.name}', status='{self.status}')>"
