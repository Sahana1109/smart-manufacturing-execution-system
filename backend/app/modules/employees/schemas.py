import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class EmployeeCreate(BaseModel):
    employee_code: str = Field(..., description="Unique employee code/identifier (e.g. EMP-001)")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    role_title: Optional[str] = Field(None, description="Operator role/title")
    is_active: Optional[bool] = Field(True, description="Active status indicator")


class EmployeeUpdate(BaseModel):
    employee_code: Optional[str] = Field(None, description="Unique employee code")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    role_title: Optional[str] = Field(None, description="Operator role/title")
    is_active: Optional[bool] = Field(None, description="Active status indicator")


class EmployeeResponse(BaseModel):
    id: uuid.UUID
    employee_code: str
    first_name: str
    last_name: str
    role_title: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
