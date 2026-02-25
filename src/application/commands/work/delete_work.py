from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.ports.transaction import EntitySaver, Transaction
from src.application.ports.work_reader import WorkReader
from src.entities.employees.models import Employee
from src.entities.works.models import WorkUUID

logger = structlog.get_logger("delete_work").bind(service="work")


@dataclass(frozen=True, slots=True)
class DeleteWorkCommand:
    uuid: UUID


class DeleteWorkCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        work_reader: WorkReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._work_reader = work_reader

    async def run(self, data: DeleteWorkCommand, current_employee: Employee) -> None:
        work = await ensure_exists(
            self._work_reader.read_by_uuid,
            WorkUUID(data.uuid),
            f"Work with uuid {data.uuid}",
        )

        await self._entity_saver.delete(work)
        await self._transaction.commit()
        logger.info("Work deleted successfully", work_uuid=str(data.uuid))
