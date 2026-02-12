from typing import Optional
from pydantic import BaseModel, Field

class CreateClientSchema(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = None
    telegram_nick: Optional[str] = None
    comment: Optional[str] = None
