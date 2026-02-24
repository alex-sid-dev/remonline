from uuid import UUID

from pydantic import BaseModel


class CreatePaymentSchema(BaseModel):
    order_uuid: UUID
    amount: float
    payment_method: str
    employee_uuid: UUID | None = None
    comment: str | None = None


class UpdatePaymentSchema(BaseModel):
    amount: float | None = None
    payment_method: str | None = None
    employee_uuid: UUID | None = None
    comment: str | None = None
