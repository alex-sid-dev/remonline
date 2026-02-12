from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class CreateOrderSchema(BaseModel):
    client_uuid: UUID
    device_uuid: UUID
    problem_description: Optional[str] = None
    comment: Optional[str] = None
    assigned_employee_uuid: Optional[UUID] = None
    status: str = "new"
    price: Optional[float] = None
