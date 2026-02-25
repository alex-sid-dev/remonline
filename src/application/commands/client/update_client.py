from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.ports.client_reader import ClientReader
from src.application.ports.transaction import Transaction
from src.entities.clients.models import ClientUUID
from src.entities.clients.services import ClientService
from src.entities.employees.models import Employee

logger = structlog.get_logger("update_client").bind(service="client")


@dataclass(frozen=True, slots=True)
class UpdateClientCommand:
    uuid: UUID
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    telegram_nick: str | None = None
    comment: str | None = None
    address: str | None = None
    is_active: bool | None = None


class UpdateClientCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        client_reader: ClientReader,
        client_service: ClientService,
    ) -> None:
        self._transaction = transaction
        self._client_reader = client_reader
        self._client_service = client_service

    async def run(self, data: UpdateClientCommand, current_employee: Employee) -> None:
        client = await ensure_exists(
            self._client_reader.read_by_uuid,
            ClientUUID(data.uuid),
            f"Client with uuid {data.uuid}",
        )

        self._client_service.update_client(
            client=client,
            full_name=data.full_name,
            phone=data.phone,
            email=data.email,
            telegram_nick=data.telegram_nick,
            comment=data.comment,
            address=data.address,
            is_active=data.is_active,
        )
        await self._transaction.commit()
        logger.info("Client updated successfully", client_uuid=str(data.uuid))
