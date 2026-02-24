from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import ConflictError
from src.application.ports.client_reader import ClientReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.clients.services import ClientService

logger = structlog.get_logger("create_client").bind(service="client")


@dataclass
class CreateClientCommandResponse:
    uuid: UUID


@dataclass
class CreateClientCommand:
    full_name: str
    phone: str
    email: str | None = None
    telegram_nick: str | None = None
    comment: str | None = None
    address: str | None = None


class CreateClientCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        client_service: ClientService,
        client_reader: ClientReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._client_reader = client_reader
        self._client_service = client_service

    async def run(self, data: CreateClientCommand) -> CreateClientCommandResponse:
        existing_client = await self._client_reader.read_by_phone(data.phone)
        if existing_client:
            raise ConflictError(message=f"Client with phone {data.phone} already exists")

        client = self._client_service.create_client(
            full_name=data.full_name,
            phone=data.phone,
            email=data.email,
            telegram_nick=data.telegram_nick,
            comment=data.comment,
            address=data.address,
        )
        self._entity_saver.add_one(client)
        await self._transaction.commit()
        logger.info("Client created successfully", client_uuid=str(client.uuid))
        return CreateClientCommandResponse(
            uuid=client.uuid,
        )
