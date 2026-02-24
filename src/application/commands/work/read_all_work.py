from dataclasses import dataclass

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.work_reader import WorkReader
from src.entities.employees.models import Employee
from src.entities.works.models import Work

logger = structlog.get_logger("read_all_work").bind(service="work")


@dataclass
class ReadAllWorkCommand:
    pass


@dataclass
class ReadWorkResponse:
    uuid: str
    order_id: int
    title: str
    employee_id: int | None
    description: str | None
    price: float | None

    @classmethod
    def from_entity(cls, entity: Work) -> "ReadWorkResponse":
        return cls(
            uuid=str(entity.uuid),
            order_id=entity.order_id,
            title=entity.title,
            employee_id=entity.employee_id,
            description=entity.description,
            price=entity.price,
        )


class ReadAllWorkCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        work_reader: WorkReader,
    ) -> None:
        self._work_reader = work_reader

    async def run(
        self, data: ReadAllWorkCommand, current_employee: Employee
    ) -> list[ReadWorkResponse]:
        works = await self._work_reader.read_all_active()
        return [ReadWorkResponse.from_entity(w) for w in works]
