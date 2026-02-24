from dataclasses import dataclass

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.employee_reader import EmployeeReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_employee").bind(service="employee")


@dataclass
class ReadAllEmployeeCommand:
    limit: int = 200
    offset: int = 0


@dataclass
class ReadEmployeeResponse:
    uuid: str
    full_name: str
    phone: str | None
    position: EmployeePosition
    salary: float | None = None
    profit_percent: float | None = None

    @classmethod
    def from_entity(cls, entity: Employee) -> "ReadEmployeeResponse":
        return cls(
            uuid=str(entity.uuid),
            full_name=entity.full_name,
            phone=entity.phone,
            position=entity.position,
            salary=entity.salary,
            profit_percent=entity.profit_percent,
        )


@dataclass
class PaginatedEmployeeResponse:
    items: list[ReadEmployeeResponse]
    total: int
    limit: int
    offset: int


class ReadAllEmployeeCommandHandler(BaseCommandHandler):
    def __init__(self, employee_reader: EmployeeReader) -> None:
        self._employee_reader = employee_reader

    async def run(
        self, data: ReadAllEmployeeCommand, current_employee: Employee
    ) -> PaginatedEmployeeResponse:
        employees, total = await self._employee_reader.read_all_active(data.limit, data.offset)
        return PaginatedEmployeeResponse(
            items=[ReadEmployeeResponse.from_entity(emp) for emp in employees if emp is not None],
            total=total,
            limit=data.limit,
            offset=data.offset,
        )
