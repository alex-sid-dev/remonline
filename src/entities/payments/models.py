from dataclasses import dataclass
from typing import Optional, NewType
from uuid import UUID
from datetime import datetime

from src.entities.base_entity import BaseEntity
from src.entities.orders.models import OrderID
from src.entities.employees.models import EmployeeID

PaymentID = NewType("PaymentID", int)
PaymentUUID = NewType("PaymentUUID", UUID)


@dataclass
class Payment(BaseEntity[PaymentID, PaymentUUID]):
    order_id: OrderID
    amount: float
    payment_method: str
    employee_id: Optional[EmployeeID] = None
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
