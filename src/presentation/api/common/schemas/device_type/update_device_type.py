from typing import Optional
from pydantic import BaseModel

class UpdateDeviceTypeSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
