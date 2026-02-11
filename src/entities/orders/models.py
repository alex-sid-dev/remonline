from dataclasses import dataclass
from typing import Optional, NewType
from uuid import UUID
from datetime import datetime

from src.entities.base_entity import BaseEntity
from src.entities.clients.models import ClientID
from src.entities.devices.models import DeviceID
from src.entities.employees.models import EmployeeID

OrderID = NewType("OrderID", int)
OrderUUID = NewType("OrderUUID", UUID)


@dataclass
class Order(BaseEntity[OrderID, OrderUUID]):
    client_id: ClientID
    device_id: DeviceID
    creator_id: Optional[EmployeeID] = None
    assigned_employee_id: Optional[EmployeeID] = None
    status: str = "new"
    problem_description: Optional[str] = None
    comment: Optional[str] = None
    price: Optional[float] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
