from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.errors._base import ConflictError
from src.application.ports.client_reader import ClientReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.clients.models import ClientUUID
from src.entities.employees.models import Employee

logger = structlog.get_logger("delete_client").bind(service="client")


@dataclass(frozen=True, slots=True)
class DeleteClientCommand:
    uuid: UUID


class DeleteClientCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        client_reader: ClientReader,
        order_reader: OrderReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._client_reader = client_reader
        self._order_reader = order_reader

    async def run(self, data: DeleteClientCommand, current_employee: Employee) -> None:
        client = await ensure_exists(
            self._client_reader.read_by_uuid, ClientUUID(data.uuid),
            f"Client with uuid {data.uuid}",
        )

        orders = await self._order_reader.read_by_client_id(client.id)
        if orders:
            raise ConflictError(
                message="Нельзя удалить клиента: есть связанные заказы"
            )

        await self._entity_saver.delete(client)
        await self._transaction.commit()
        logger.info("Client deleted successfully", client_uuid=str(data.uuid))
