from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee
from src.entities.parts.models import PartUUID

logger = structlog.get_logger("delete_part").bind(service="part")


@dataclass
class DeletePartCommand:
    uuid: UUID


class DeletePartCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        part_reader: PartReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._part_reader = part_reader

    async def run(self, data: DeletePartCommand, current_employee: Employee) -> None:
        part = await self._part_reader.read_by_uuid(PartUUID(data.uuid))
        if not part:
            raise EntityNotFoundError(f"Part with uuid {data.uuid} not found")

        await self._entity_saver.delete(part)
        await self._transaction.commit()
        logger.info("Part deleted successfully", part_uuid=str(data.uuid))
