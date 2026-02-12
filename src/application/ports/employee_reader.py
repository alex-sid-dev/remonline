from typing import List, Optional, Protocol
from src.entities.employees.models import Employee, EmployeeID, EmployeeUUID
from src.entities.users.models import UserID

class EmployeeReader(Protocol):
    """Read-only repository for Employee entities."""

    async def read_by_id(self, employee_id: EmployeeID) -> Optional[Employee]:
        ...

    async def read_by_uuid(self, employee_uuid: EmployeeUUID) -> Optional[Employee]:
        ...

    async def read_by_user_id(self, user_id: UserID) -> Optional[Employee]:
        ...

    async def read_all_active(self) -> List[Employee]:
        ...
