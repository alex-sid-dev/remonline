from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.commands.employee.read_all_employee import ReadEmployeeResponse
from src.application.errors._base import EntityNotFoundError
from src.application.ports.employee_reader import EmployeeReader
from src.entities.employees.models import Employee, EmployeeUUID

logger = structlog.get_logger("read_employee").bind(service="employee")


@dataclass
class ReadEmployeeCommand:
    uuid: UUID


class ReadEmployeeCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        employee_reader: EmployeeReader,
    ) -> None:
        self._employee_reader = employee_reader

    async def run(
        self, data: ReadEmployeeCommand, current_employee: Employee
    ) -> ReadEmployeeResponse:
        employee = await self._employee_reader.read_by_uuid(EmployeeUUID(data.uuid))
        if not employee:
            raise EntityNotFoundError(f"Employee with uuid {data.uuid} not found")

        return ReadEmployeeResponse.from_entity(employee)
