from dataclasses import dataclass
from typing import List, Optional
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.client_reader import ClientReader
from src.entities.clients.models import Client
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_client").bind(service="client")


@dataclass
class ReadAllClientCommand:
    limit: int = 200
    offset: int = 0


@dataclass
class ReadClientResponse:
    uuid: str
    full_name: str
    phone: str
    email: Optional[str]
    telegram_nick: Optional[str]
    comment: Optional[str]
    address: Optional[str]

    @classmethod
    def from_entity(cls, entity: Client) -> "ReadClientResponse":
        return cls(
            uuid=str(entity.uuid),
            full_name=entity.full_name,
            phone=entity.phone,
            email=entity.email,
            telegram_nick=entity.telegram_nick,
            comment=entity.comment,
            address=entity.address,
        )


@dataclass
class PaginatedClientResponse:
    items: List[ReadClientResponse]
    total: int
    limit: int
    offset: int


class ReadAllClientCommandHandler(BaseCommandHandler):
    def __init__(self, client_reader: ClientReader) -> None:
        self._client_reader = client_reader

    async def run(self, data: ReadAllClientCommand, current_employee: Employee) -> PaginatedClientResponse:
        clients, total = await self._client_reader.read_all_active(data.limit, data.offset)
        return PaginatedClientResponse(
            items=[ReadClientResponse.from_entity(c) for c in clients],
            total=total,
            limit=data.limit,
            offset=data.offset,
        )
