from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands.client.read_all_client import ReadClientResponse
from src.application.ports.client_reader import ClientReader
from src.entities.clients.models import ClientUUID
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_client").bind(service="client")


@dataclass(frozen=True, slots=True)
class ReadClientCommand:
    uuid: UUID


class ReadClientCommandHandler:
    def __init__(
        self,
        client_reader: ClientReader,
    ) -> None:
        self._client_reader = client_reader

    async def run(self, data: ReadClientCommand, current_employee: Employee) -> ReadClientResponse:
        client = await ensure_exists(
            self._client_reader.read_by_uuid,
            ClientUUID(data.uuid),
            f"Client with uuid {data.uuid}",
        )
        return ReadClientResponse.model_validate(client)
