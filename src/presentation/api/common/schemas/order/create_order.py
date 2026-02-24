from uuid import UUID

from pydantic import BaseModel
from src.entities.orders.enum import OrderStatus


class CreateOrderSchema(BaseModel):
    client_uuid: UUID
    device_uuid: UUID
    problem_description: str | None = None
    assigned_employee_uuid: UUID | None = None
    manager_uuid: UUID | None = None
    status: OrderStatus = OrderStatus.NEW
    price: float | None = None
