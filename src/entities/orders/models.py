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

from dataclasses import dataclass, field
from typing import Optional, List


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

    # Поля для автоподгрузки (SQLAlchemy заполнит их сам)
    # init=False исключает их из конструктора __init__
    client: "Client" = field(init=False)
    device: "Device" = field(init=False)
    creator: Optional["Employee"] = field(init=False, default=None)
    assigned_employee: Optional["Employee"] = field(init=False, default=None)

    comments: List["OrderComment"] = field(init=False, default_factory=list)
    payments: List["Payment"] = field(init=False, default_factory=list)
