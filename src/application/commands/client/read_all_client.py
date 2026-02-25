from dataclasses import dataclass
from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict

from src.application.ports.client_reader import ClientReader
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_client").bind(service="client")


@dataclass(frozen=True, slots=True)
class ReadAllClientCommand:
    limit: int = 200
    offset: int = 0


class ReadClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    full_name: str
    phone: str
    email: str | None = None
    telegram_nick: str | None = None
    comment: str | None = None
    address: str | None = None


class PaginatedClientResponse(BaseModel):
    items: list[ReadClientResponse]
    total: int
    limit: int
    offset: int


class ReadAllClientCommandHandler:
    def __init__(self, client_reader: ClientReader) -> None:
        self._client_reader = client_reader

    async def run(
        self, data: ReadAllClientCommand, current_employee: Employee
    ) -> PaginatedClientResponse:
        clients, total = await self._client_reader.read_all_active(data.limit, data.offset)
        return PaginatedClientResponse(
            items=[ReadClientResponse.model_validate(c) for c in clients],
            total=total,
            limit=data.limit,
            offset=data.offset,
        )
