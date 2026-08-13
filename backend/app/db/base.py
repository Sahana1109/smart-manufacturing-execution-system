from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, func, BigInteger


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy declarative models in SmartMES.
    """
    pass


class TimestampMixin:
    """
    Mixin providing standard created_at and updated_at timestamps.
    """
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
