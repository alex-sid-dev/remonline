from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.commands.work.read_all_work import ReadWorkResponse
from src.application.errors._base import EntityNotFoundError
from src.application.ports.work_reader import WorkReader
from src.entities.employees.models import Employee
from src.entities.works.models import WorkUUID

logger = structlog.get_logger("read_work").bind(service="work")


@dataclass
class ReadWorkCommand:
    uuid: UUID


class ReadWorkCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        work_reader: WorkReader,
    ) -> None:
        self._work_reader = work_reader

    async def run(self, data: ReadWorkCommand, current_employee: Employee) -> ReadWorkResponse:
        work = await self._work_reader.read_by_uuid(WorkUUID(data.uuid))
        if not work:
            raise EntityNotFoundError(f"Work with uuid {data.uuid} not found")

        return ReadWorkResponse.from_entity(work)
