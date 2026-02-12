from dataclasses import dataclass
from typing import List, Optional

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.commands.employee.update_employee import UpdateEmployeeCommand
from src.application.ports.employee_reader import EmployeeReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_employee").bind(service="employee")


@dataclass
class ReadAllEmployeeCommand:
    pass


@dataclass
class ReadEmployeeResponse:
    full_name: str
    phone: Optional[str]
    position: EmployeePosition

    @classmethod
    def from_entity(cls, entity: Employee) -> "ReadEmployeeResponse":
        return cls(
            full_name=entity.full_name,
            phone=entity.phone,
            position=entity.position
        )


class ReadAllEmployeeCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            employee_reader: EmployeeReader,
    ) -> None:
        self._employee_reader = employee_reader

    async def run(self, data: ReadAllEmployeeCommand, current_employee: Employee) -> List[ReadEmployeeResponse]:
        employees = await self._employee_reader.read_all_active()
        response = [
            ReadEmployeeResponse.from_entity(emp)
            for emp in employees if emp is not None
        ]
        return response
