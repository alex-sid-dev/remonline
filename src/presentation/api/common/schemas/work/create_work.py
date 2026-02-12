from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class CreateWorkSchema(BaseModel):
    order_uuid: UUID
    title: str
    employee_uuid: Optional[UUID] = None
    description: Optional[str] = None
    price: Optional[float] = None

class UpdateWorkSchema(BaseModel):
    title: Optional[str] = None
    employee_uuid: Optional[UUID] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
