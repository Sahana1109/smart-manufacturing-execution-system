import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


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
