import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
from app.modules.users.models import GUID


class Employee(Base, TimestampMixin):
    """
    SmartMES Employee Entity Model
    """
    __tablename__ = "employees"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    employee_code = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role_title = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    work_orders = relationship("WorkOrder", back_populates="assigned_employee")

    def __repr__(self) -> str:
        return f"<Employee(code='{self.employee_code}', name='{self.first_name} {self.last_name}')>"
