from uuid import UUID

from pydantic import BaseModel
from src.entities.orders.enum import OrderStatus


class UpdateOrderSchema(BaseModel):
    assigned_employee_uuid: UUID | None = None
    creator_uuid: UUID | None = None
    status: OrderStatus | None = None
    problem_description: str | None = None
    price: float | None = None
    is_active: bool | None = None
