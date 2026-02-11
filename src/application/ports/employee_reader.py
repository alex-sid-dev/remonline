from abc import ABC, abstractmethod
from typing import List
from src.entities.employees.models import Employee, EmployeeID
from src.entities.users.models import UserID

class EmployeeReader(ABC):
    """Read-only repository for Employee entities."""

    @abstractmethod
    async def read_by_oid(self, employee_oid: EmployeeID) -> Employee | None: ...

    @abstractmethod
    async def read_by_user_oid(self, user_oid: UserID) -> Employee | None: ...

    @abstractmethod
    async def read_all_active(self) -> List[Employee] | None: ...
