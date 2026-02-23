from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UpdateDeviceSchema(BaseModel):
    brand_uuid: Optional[UUID] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
