from typing import Final

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.employee_reader import EmployeeReader
from src.entities.employees.models import Employee, EmployeeID, EmployeeUUID
from src.entities.users.models import UserID
from src.infra.models.employees import employees_table


class EmployeeReaderAdapter(EmployeeReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final = session
        self._logger = structlog.get_logger("db").bind(service="db", entity="employee")

    async def read_by_id(self, employee_id: EmployeeID) -> Employee | None:
        self._logger.info("Reading employee by ID", employee_id=str(employee_id))
        stmt = select(Employee).where(employees_table.c.employee_id == employee_id)
        result = await self._session.execute(stmt)
        employee = result.scalar_one_or_none()
        if employee is None:
            self._logger.warning("Employee not found by ID", employee_id=str(employee_id))
        else:
            self._logger.info("Employee found", employee_id=str(employee.id))
        return employee

    async def read_by_uuid(self, employee_uuid: EmployeeUUID) -> Employee | None:
        self._logger.info("Reading employee by UUID", employee_uuid=str(employee_uuid))
        stmt = select(Employee).where(employees_table.c.employee_uuid == employee_uuid)
        result = await self._session.execute(stmt)
        employee = result.scalar_one_or_none()
        if employee is None:
            self._logger.warning("Employee not found by UUID", employee_uuid=str(employee_uuid))
        else:
            self._logger.info("Employee found", employee_id=str(employee.id))
        return employee

    async def read_by_user_id(self, user_id: UserID) -> Employee | None:
        self._logger.info("Reading employee by User ID", user_id=str(user_id))
        stmt = select(Employee).where(employees_table.c.user_id == user_id)
        result = await self._session.execute(stmt)
        employee = result.scalar_one_or_none()
        if employee is None:
            self._logger.warning("Employee not found by User ID", user_id=str(user_id))
        else:
            self._logger.info("Employee found", employee_id=str(employee.id))
        return employee

    async def read_all_active(
        self, limit: int = 200, offset: int = 0
    ) -> tuple[list[Employee], int]:
        self._logger.info("Reading all active employees")
        count_stmt = (
            select(func.count())
            .select_from(employees_table)
            .where(employees_table.c.is_active.is_(True))
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Employee)
            .where(employees_table.c.is_active.is_(True))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        employees = list(result.scalars().all())
        self._logger.info("Active employees found", count=len(employees), total=total)
        return employees, total
