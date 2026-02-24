from dataclasses import dataclass

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.part_reader import PartReader
from src.entities.employees.models import Employee
from src.entities.parts.models import Part

logger = structlog.get_logger("read_all_part").bind(service="part")


@dataclass
class ReadAllPartCommand:
    limit: int = 200
    offset: int = 0


@dataclass
class ReadPartResponse:
    uuid: str
    name: str
    sku: str | None
    price: float | None
    stock_qty: int | None

    @classmethod
    def from_entity(cls, entity: Part) -> "ReadPartResponse":
        return cls(
            uuid=str(entity.uuid),
            name=entity.name,
            sku=entity.sku,
            price=entity.price,
            stock_qty=entity.stock_qty,
        )


@dataclass
class PaginatedPartResponse:
    items: list[ReadPartResponse]
    total: int
    limit: int
    offset: int


class ReadAllPartCommandHandler(BaseCommandHandler):
    def __init__(self, part_reader: PartReader) -> None:
        self._part_reader = part_reader

    async def run(
        self, data: ReadAllPartCommand, current_employee: Employee
    ) -> PaginatedPartResponse:
        parts, total = await self._part_reader.read_all_active(data.limit, data.offset)
        return PaginatedPartResponse(
            items=[ReadPartResponse.from_entity(p) for p in parts],
            total=total,
            limit=data.limit,
            offset=data.offset,
        )
