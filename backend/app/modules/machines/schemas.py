import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MachineCreate(BaseModel):
    machine_code: str = Field(..., description="Unique machine code/identifier (e.g. MAC-CNC-01)")
    name: str = Field(..., description="Machine name or model specification")
    status: Optional[str] = Field("OPERATIONAL", description="Status: OPERATIONAL, AVAILABLE, IN_USE, MAINTENANCE, INACTIVE")
    is_active: Optional[bool] = Field(True, description="Active status indicator")


class MachineUpdate(BaseModel):
    machine_code: Optional[str] = Field(None, description="Unique machine code/identifier")
    name: Optional[str] = Field(None, description="Machine name")
    status: Optional[str] = Field(None, description="Status: OPERATIONAL, AVAILABLE, IN_USE, MAINTENANCE, INACTIVE")
    is_active: Optional[bool] = Field(None, description="Active status indicator")


class MachineStatusUpdate(BaseModel):
    status: str = Field(..., description="New machine status: OPERATIONAL, AVAILABLE, IN_USE, MAINTENANCE, INACTIVE")


class MachineResponse(BaseModel):
    id: uuid.UUID
    machine_code: str
    name: str
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
