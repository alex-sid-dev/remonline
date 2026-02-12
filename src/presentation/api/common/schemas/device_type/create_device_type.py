from typing import Optional
from pydantic import BaseModel

class CreateDeviceTypeSchema(BaseModel):
    name: str
    description: str = ""
