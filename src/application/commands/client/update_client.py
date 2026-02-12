from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.client_reader import ClientReader
from src.application.ports.transaction import Transaction
from src.entities.clients.models import ClientUUID
from src.entities.clients.services import ClientService
from src.entities.employees.models import Employee
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("update_client").bind(service="client")

@dataclass
class UpdateClientCommand:
    uuid: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class UpdateClientCommandHandler(BaseCommandHandler):
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
        client = await self._client_reader.read_by_uuid(ClientUUID(data.uuid))
        if not client:
            raise EntityNotFoundError(f"Client with uuid {data.uuid} not found")

        self._client_service.update_client(
            client=client,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            email=data.email,
            is_active=data.is_active
        )
        await self._transaction.commit()
        logger.info("Client updated successfully", client_uuid=str(data.uuid))
