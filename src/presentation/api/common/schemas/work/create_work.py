from uuid import UUID

from pydantic import BaseModel


class CreateWorkSchema(BaseModel):
    order_uuid: UUID
    title: str
    employee_uuid: UUID | None = None
    description: str | None = None
    price: float | None = None
    qty: int = 1


class UpdateWorkSchema(BaseModel):
    title: str | None = None
    employee_uuid: UUID | None = None
    description: str | None = None
    price: float | None = None
    qty: int | None = None
    is_active: bool | None = None
