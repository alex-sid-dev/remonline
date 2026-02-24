from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.client_reader import ClientReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.clients.models import ClientUUID
from src.entities.employees.models import Employee

logger = structlog.get_logger("delete_client").bind(service="client")


@dataclass
class DeleteClientCommand:
    uuid: UUID


class DeleteClientCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        client_reader: ClientReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._client_reader = client_reader

    async def run(self, data: DeleteClientCommand, current_employee: Employee) -> None:
        client = await self._client_reader.read_by_uuid(ClientUUID(data.uuid))
        if not client:
            raise EntityNotFoundError(f"Client with uuid {data.uuid} not found")

        await self._entity_saver.delete(client)
        await self._transaction.commit()
        logger.info("Client deleted successfully", client_uuid=str(data.uuid))
