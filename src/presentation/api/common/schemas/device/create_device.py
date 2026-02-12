from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class CreateDeviceSchema(BaseModel):
    client_uuid: UUID
    type_uuid: UUID
    brand: str
    model: str
    serial_number: Optional[str] = None
    description: Optional[str] = None
