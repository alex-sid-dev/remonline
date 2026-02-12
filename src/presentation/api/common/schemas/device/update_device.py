from typing import Optional
from pydantic import BaseModel

class UpdateDeviceSchema(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
