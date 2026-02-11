from dataclasses import dataclass
from typing import Optional, NewType
from uuid import UUID

from sqlalchemy.orm import Mapped

from src.entities.base_entity import BaseEntity
from src.entities.employees.enum import EmployeePosition
from src.entities.users.models import UserID

EmployeeID = NewType("EmployeeID", int)
EmployeeUUID = NewType("EmployeeUUID", UUID)


@dataclass
class Employee(BaseEntity[EmployeeID, EmployeeUUID]):
    user_id: UserID
    full_name: str
    phone: Optional[str]
    position: EmployeePosition
    is_active: bool
