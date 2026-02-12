from dataclasses import dataclass
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.part_reader import PartReader
from src.entities.parts.models import PartUUID
from src.entities.employees.models import Employee
from src.application.commands.part.read_all_part import ReadPartResponse
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("read_part").bind(service="part")

@dataclass
class ReadPartCommand:
    uuid: UUID

class ReadPartCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            part_reader: PartReader,
    ) -> None:
        self._part_reader = part_reader

    async def run(self, data: ReadPartCommand, current_employee: Employee) -> ReadPartResponse:
        part = await self._part_reader.read_by_uuid(PartUUID(data.uuid))
        if not part:
            raise EntityNotFoundError(f"Part with uuid {data.uuid} not found")
            
        return ReadPartResponse.from_entity(part)
