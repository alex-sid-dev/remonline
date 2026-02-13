from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.client_reader import ClientReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.clients.services import ClientService
from src.entities.employees.models import Employee

from src.application.errors._base import ConflictError

logger = structlog.get_logger("create_client").bind(service="client")


@dataclass
class CreateClientCommandResponse:
    uuid: UUID


@dataclass
class CreateClientCommand:
    full_name: str
    phone: str
    email: Optional[str] = None
    telegram_nick: Optional[str] = None
    comment: Optional[str] = None


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
            comment=data.comment
        )
        self._entity_saver.add_one(client)
        await self._transaction.commit()
        logger.info("Client created successfully", client_uuid=str(client.uuid))
        return CreateClientCommandResponse(
            uuid=client.uuid,
        )
