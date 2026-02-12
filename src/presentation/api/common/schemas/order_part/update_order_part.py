from typing import Optional
from pydantic import BaseModel, Field

class UpdateOrderPartSchema(BaseModel):
    qty: Optional[int] = Field(None, description="Quantity of parts")
    price: Optional[float] = Field(None, description="Price per unit")
