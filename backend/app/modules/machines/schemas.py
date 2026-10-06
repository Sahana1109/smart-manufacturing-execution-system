import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MachineResponse(BaseModel):
    id: uuid.UUID
    machine_code: str
    name: str
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
