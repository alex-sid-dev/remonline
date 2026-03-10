from dataclasses import dataclass
from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict

from src.application.ports.employee_reader import EmployeeReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_employee").bind(service="employee")


@dataclass(frozen=True, slots=True)
class ReadAllEmployeeCommand:
    limit: int = 200
    offset: int = 0


class ReadEmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    full_name: str
    phone: str | None = None
    position: EmployeePosition
    salary: float | None = None
    profit_percent: float | None = None


class PaginatedEmployeeResponse(BaseModel):
    items: list[ReadEmployeeResponse]
    total: int
    limit: int
    offset: int


class ReadAllEmployeeCommandHandler:
    def __init__(self, employee_reader: EmployeeReader) -> None:
        self._employee_reader = employee_reader

    async def run(
        self,
        data: ReadAllEmployeeCommand,
        current_employee: Employee,
    ) -> PaginatedEmployeeResponse:
        employees, total = await self._employee_reader.read_all_active(
            organization_id=current_employee.organization_id,
            limit=data.limit,
            offset=data.offset,
        )
        return PaginatedEmployeeResponse(
            items=[
                ReadEmployeeResponse.model_validate(emp) for emp in employees if emp is not None
            ],
            total=total,
            limit=data.limit,
            offset=data.offset,
        )
