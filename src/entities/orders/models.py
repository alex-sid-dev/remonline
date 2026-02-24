from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.clients.models import ClientID
from src.entities.devices.models import DeviceID
from src.entities.employees.models import EmployeeID
from src.entities.orders.enum import OrderStatus

OrderID = NewType("OrderID", int)
OrderUUID = NewType("OrderUUID", UUID)


@dataclass
class Order(BaseEntity[OrderID, OrderUUID]):
    client_id: ClientID
    device_id: DeviceID
    creator_id: EmployeeID | None = None
    assigned_employee_id: EmployeeID | None = None
    status: OrderStatus = OrderStatus.NEW
    problem_description: str | None = None
    price: float | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
