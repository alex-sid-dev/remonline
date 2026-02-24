from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.employees.enum import EmployeePosition
from src.entities.users.models import UserID

EmployeeID = NewType("EmployeeID", int)
EmployeeUUID = NewType("EmployeeUUID", UUID)


@dataclass
class Employee(BaseEntity[EmployeeID, EmployeeUUID]):
    user_id: UserID
    full_name: str
    phone: str | None
    position: EmployeePosition
    is_active: bool
    salary: float | None = None
    profit_percent: float | None = None
