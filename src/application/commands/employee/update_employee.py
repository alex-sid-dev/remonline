from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import EmployeeUUID, Employee
from src.entities.employees.services import EmployeeService
from src.application.errors._base import PermissionDeniedError
from src.application.errors.employee import EmployeeNotFoundError

logger = structlog.get_logger("update_employee").bind(service="employee")


@dataclass
class UpdateEmployeeCommand:
    uuid: UUID
    full_name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[EmployeePosition] = None


class UpdateEmployeeCommandHandler(BaseCommandHandler):
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
        # Только супервизор может назначать роль supervisor.
        if data.position == EmployeePosition.SUPERVISOR and current_employee.position != EmployeePosition.SUPERVISOR:
            raise PermissionDeniedError(message="Только супервизор может назначать роль «супервизор».")
        employee_to_update = await self._employee_reader.read_by_uuid(EmployeeUUID(data.uuid))
        if not employee_to_update:
            raise EmployeeNotFoundError()

        self._employee_service.update_employee(
            employee=employee_to_update,
            full_name=data.full_name,
            phone=data.phone,
            position=data.position,
        )
        await self._transaction.commit()
        logger.info("Employee updated successfully", employee_uuid=str(data.uuid))
