from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.entities.orders.enum import OrderStatus


class CreateOrderSchema(BaseModel):
    client_uuid: UUID
    device_uuid: UUID
    problem_description: Optional[str] = None
    assigned_employee_uuid: Optional[UUID] = None
    manager_uuid: Optional[UUID] = None
    status: OrderStatus = OrderStatus.NEW
    price: Optional[float] = None
