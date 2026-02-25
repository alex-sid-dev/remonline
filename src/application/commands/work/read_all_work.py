from dataclasses import dataclass
from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict

from src.application.ports.work_reader import WorkReader
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_work").bind(service="work")


@dataclass(frozen=True, slots=True)
class ReadAllWorkCommand:
    pass


class ReadWorkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    order_id: int
    title: str
    employee_id: int | None = None
    description: str | None = None
    price: float | None = None


class ReadAllWorkCommandHandler:
    def __init__(
        self,
        work_reader: WorkReader,
    ) -> None:
        self._work_reader = work_reader

    async def run(
        self, data: ReadAllWorkCommand, current_employee: Employee
    ) -> list[ReadWorkResponse]:
        works = await self._work_reader.read_all_active()
        return [ReadWorkResponse.model_validate(w) for w in works]
