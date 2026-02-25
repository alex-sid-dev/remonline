from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands.employee.read_all_employee import ReadEmployeeResponse
from src.application.ports.employee_reader import EmployeeReader
from src.entities.employees.models import Employee, EmployeeUUID

logger = structlog.get_logger("read_employee").bind(service="employee")


@dataclass(frozen=True, slots=True)
class ReadEmployeeCommand:
    uuid: UUID


class ReadEmployeeCommandHandler:
    def __init__(
        self,
        employee_reader: EmployeeReader,
    ) -> None:
        self._employee_reader = employee_reader

    async def run(
        self, data: ReadEmployeeCommand, current_employee: Employee
    ) -> ReadEmployeeResponse:
        employee = await ensure_exists(
            self._employee_reader.read_by_uuid, EmployeeUUID(data.uuid),
            f"Employee with uuid {data.uuid}",
        )
        return ReadEmployeeResponse.model_validate(employee)
