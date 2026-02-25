from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands.part.read_all_part import ReadPartResponse
from src.application.ports.part_reader import PartReader
from src.entities.employees.models import Employee
from src.entities.parts.models import PartUUID

logger = structlog.get_logger("read_part").bind(service="part")


@dataclass(frozen=True, slots=True)
class ReadPartCommand:
    uuid: UUID


class ReadPartCommandHandler:
    def __init__(
        self,
        part_reader: PartReader,
    ) -> None:
        self._part_reader = part_reader

    async def run(self, data: ReadPartCommand, current_employee: Employee) -> ReadPartResponse:
        part = await ensure_exists(
            self._part_reader.read_by_uuid,
            PartUUID(data.uuid),
            f"Part with uuid {data.uuid}",
        )
        return ReadPartResponse.model_validate(part)
