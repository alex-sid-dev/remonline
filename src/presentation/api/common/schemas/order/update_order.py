from typing import Optional

from pydantic import BaseModel

from src.entities.orders.enum import OrderStatus


class UpdateOrderSchema(BaseModel):
    assigned_employee_id: Optional[int] = None
    creator_id: Optional[int] = None
    status: Optional[OrderStatus] = None
    problem_description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
