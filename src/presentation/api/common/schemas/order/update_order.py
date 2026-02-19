from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.entities.orders.enum import OrderStatus


class UpdateOrderSchema(BaseModel):
    assigned_employee_uuid: Optional[UUID] = None
    creator_uuid: Optional[UUID] = None
    status: Optional[OrderStatus] = None
    problem_description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
