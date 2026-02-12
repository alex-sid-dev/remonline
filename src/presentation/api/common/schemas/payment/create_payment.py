from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class CreatePaymentSchema(BaseModel):
    order_uuid: UUID
    amount: float
    payment_method: str
    employee_uuid: Optional[UUID] = None
    comment: Optional[str] = None

class UpdatePaymentSchema(BaseModel):
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    employee_uuid: Optional[UUID] = None
    comment: Optional[str] = None
