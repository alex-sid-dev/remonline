from typing import Optional
from pydantic import BaseModel

class CreatePartSchema(BaseModel):
    name: str
    sku: Optional[str] = None
    price: Optional[float] = None
    stock_qty: Optional[int] = None

class UpdatePartSchema(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    stock_qty: Optional[int] = None
    is_active: Optional[bool] = None
