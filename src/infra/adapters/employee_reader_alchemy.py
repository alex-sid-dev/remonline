import structlog
from typing import Final, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.employees.models import Employee, EmployeeID, EmployeeUUID
from src.entities.users.models import UserID
from src.infra.models.employees import employees_table
from src.application.ports.employee_reader import EmployeeReader


class EmployeeReaderAlchemy(EmployeeReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final = session
        self._logger = structlog.get_logger("db").bind(service="db", entity="employee")

    async def read_by_id(self, employee_id: EmployeeID) -> Optional[Employee]:
        self._logger.info("Reading employee by ID", employee_id=str(employee_id))
        stmt = select(Employee).where(employees_table.c.employee_id == employee_id)
        result = await self._session.execute(stmt)
        employee = result.scalar_one_or_none()
        if employee is None:
            self._logger.warning("Employee not found by ID", employee_id=str(employee_id))
        else:
            self._logger.info("Employee found", employee_id=str(employee.id))
        return employee

    async def read_by_uuid(self, employee_uuid: EmployeeUUID) -> Optional[Employee]:
        self._logger.info("Reading employee by UUID", employee_uuid=str(employee_uuid))
        stmt = select(Employee).where(employees_table.c.employee_uuid == employee_uuid)
        result = await self._session.execute(stmt)
        employee = result.scalar_one_or_none()
        if employee is None:
            self._logger.warning("Employee not found by UUID", employee_uuid=str(employee_uuid))
        else:
            self._logger.info("Employee found", employee_id=str(employee.id))
        return employee

    async def read_by_user_id(self, user_id: UserID) -> Optional[Employee]:
        self._logger.info("Reading employee by User ID", user_id=str(user_id))
        stmt = select(Employee).where(employees_table.c.user_id == user_id)
        result = await self._session.execute(stmt)
        employee = result.scalar_one_or_none()
        if employee is None:
            self._logger.warning("Employee not found by User ID", user_id=str(user_id))
        else:
            self._logger.info("Employee found", employee_id=str(employee.id))
        return employee

    async def read_all_active(self) -> List[Employee]:
        self._logger.info("Reading all active employees")
        stmt = select(Employee).where(employees_table.c.is_active == True)
        result = await self._session.execute(stmt)
        employees = list(result.scalars().all())
        self._logger.info("Number of active employees found", count=len(employees))
        return employees
