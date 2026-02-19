from typing import Optional
from pydantic import BaseModel, Field

class UpdateClientSchema(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[str] = None
    telegram_nick: Optional[str] = None
    comment: Optional[str] = None
    address: Optional[str] = Field(None, max_length=1024)
    is_active: Optional[bool] = None
