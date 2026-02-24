from typing import Protocol

from src.entities.employees.models import Employee, EmployeeID, EmployeeUUID
from src.entities.users.models import UserID


class EmployeeReader(Protocol):
    async def read_by_id(self, employee_id: EmployeeID) -> Employee | None: ...

    async def read_by_uuid(self, employee_uuid: EmployeeUUID) -> Employee | None: ...

    async def read_by_user_id(self, user_id: UserID) -> Employee | None: ...

    async def read_all_active(
        self, limit: int = 200, offset: int = 0
    ) -> tuple[list[Employee], int]: ...
