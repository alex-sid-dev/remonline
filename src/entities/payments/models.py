from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.employees.models import EmployeeID
from src.entities.orders.models import OrderID
from src.entities.organizations.models import OrganizationID

PaymentID = NewType("PaymentID", int)
PaymentUUID = NewType("PaymentUUID", UUID)


@dataclass
class Payment(BaseEntity[PaymentID, PaymentUUID]):
    order_id: OrderID
    amount: float
    payment_method: str
    organization_id: OrganizationID
    employee_id: EmployeeID | None = None
    comment: str | None = None
    created_at: datetime | None = None
