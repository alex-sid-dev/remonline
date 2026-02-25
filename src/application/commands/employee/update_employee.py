from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands._permissions import (
    assert_can_assign_supervisor,
    assert_can_change_salary,
    assert_can_modify_target,
)
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee, EmployeeUUID
from src.entities.employees.services import EmployeeService

logger = structlog.get_logger("update_employee").bind(service="employee")


@dataclass(frozen=True, slots=True)
class UpdateEmployeeCommand:
    uuid: UUID
    full_name: str | None = None
    phone: str | None = None
    position: EmployeePosition | None = None
    salary: float | None = None
    profit_percent: float | None = None


class UpdateEmployeeCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        employee_reader: EmployeeReader,
        employee_service: EmployeeService,
    ) -> None:
        self._transaction = transaction
        self._employee_reader = employee_reader
        self._employee_service = employee_service

    async def run(self, data: UpdateEmployeeCommand, current_employee: Employee) -> None:
        if data.position == EmployeePosition.SUPERVISOR:
            assert_can_assign_supervisor(current_employee)

        if data.salary is not None or data.profit_percent is not None:
            assert_can_change_salary(current_employee)

        employee_to_update = await ensure_exists(
            self._employee_reader.read_by_uuid,
            EmployeeUUID(data.uuid),
            "Employee",
        )

        assert_can_modify_target(current_employee, employee_to_update)

        self._employee_service.update_employee(
            employee=employee_to_update,
            full_name=data.full_name,
            phone=data.phone,
            position=data.position,
            salary=data.salary,
            profit_percent=data.profit_percent,
        )
        await self._transaction.commit()
        logger.info("Employee updated successfully", employee_uuid=str(data.uuid))
