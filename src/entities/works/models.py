from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.employees.models import EmployeeID
from src.entities.orders.models import OrderID

WorkID = NewType("WorkID", int)
WorkUUID = NewType("WorkUUID", UUID)


@dataclass
class Work(BaseEntity[WorkID, WorkUUID]):
    order_id: OrderID
    title: str
    employee_id: EmployeeID | None = None
    description: str | None = None
    price: float | None = None
    qty: int = 1
    is_active: bool = True
