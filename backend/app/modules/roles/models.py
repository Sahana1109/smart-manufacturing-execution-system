from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.modules.users.models import GUID


class UserRole(Base):
    """
    Association Table linking Users to Roles (Many-to-Many)
    """
    __tablename__ = "user_roles"

    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Role(Base):
    """
    SmartMES Security Role Model
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role(name='{self.name}')>"
