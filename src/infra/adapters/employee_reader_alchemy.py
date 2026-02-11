import structlog
from typing import Final, Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.employees.models import Employee, EmployeeID
from src.entities.users.models import UserID
from src.infra.models.employees import employees_table
from src.application.ports.employee_reader import EmployeeReader


class EmployeeReaderAlchemy(EmployeeReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final = session
        self._logger = structlog.get_logger("db").bind(service="db", entity="employee")

    async def read_by_oid(self, employee_oid: EmployeeID) -> Employee | None:
        self._logger.info("Reading employee by OID", employee_oid=str(employee_oid))
        stmt = select(Employee).where(employees_table.c.employee_id == employee_oid)
        result = await self._session.execute(stmt)
        employee = result.scalar_one_or_none()
        if employee is None:
            self._logger.warning("Employee not found by OID", employee_oid=str(employee_oid))
        else:
            self._logger.info("Employee found", employee_id=employee.oid)
        return employee

    async def read_by_user_oid(self, user_oid: UserID) -> Employee | None:
        self._logger.info("Reading employee by User OID", user_oid=str(user_oid))
        stmt = select(Employee).where(employees_table.c.user_id == user_oid)
        result = await self._session.execute(stmt)
        employee = result.scalar_one_or_none()
        if employee is None:
            self._logger.warning("Employee not found by User OID", user_oid=str(user_oid))
        else:
            self._logger.info("Employee found", employee_id=employee.oid)
        return employee

    async def read_all_active(self) -> Sequence[Any]:
        self._logger.info("Reading all active employees")
        stmt = select(Employee).where(employees_table.c.is_active == True)
        result = await self._session.execute(stmt)
        employees = result.scalars().all()
        self._logger.info("Number of active employees found", count=len(employees))
        return employees
