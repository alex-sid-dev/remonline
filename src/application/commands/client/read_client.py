from dataclasses import dataclass
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.client_reader import ClientReader
from src.entities.clients.models import ClientUUID
from src.entities.employees.models import Employee
from src.application.commands.client.read_all_client import ReadClientResponse
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("read_client").bind(service="client")

@dataclass
class ReadClientCommand:
    uuid: UUID

class ReadClientCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            client_reader: ClientReader,
    ) -> None:
        self._client_reader = client_reader

    async def run(self, data: ReadClientCommand, current_employee: Employee) -> ReadClientResponse:
        client = await self._client_reader.read_by_uuid(ClientUUID(data.uuid))
        if not client:
            raise EntityNotFoundError(f"Client with uuid {data.uuid} not found")
            
        return ReadClientResponse.from_entity(client)
