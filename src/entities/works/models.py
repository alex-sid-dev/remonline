from dataclasses import dataclass
from typing import Optional, NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.orders.models import OrderID
from src.entities.employees.models import EmployeeID

WorkID = NewType("WorkID", int)
WorkUUID = NewType("WorkUUID", UUID)


@dataclass
class Work(BaseEntity[WorkID, WorkUUID]):
    order_id: OrderID
    title: str
    employee_id: Optional[EmployeeID] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: bool = True
