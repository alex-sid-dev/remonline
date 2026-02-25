from dataclasses import dataclass
from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict

from src.application.ports.part_reader import PartReader
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_part").bind(service="part")


@dataclass(frozen=True, slots=True)
class ReadAllPartCommand:
    limit: int = 200
    offset: int = 0


class ReadPartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    sku: str | None = None
    price: float | None = None
    stock_qty: int | None = None


class PaginatedPartResponse(BaseModel):
    items: list[ReadPartResponse]
    total: int
    limit: int
    offset: int


class ReadAllPartCommandHandler:
    def __init__(self, part_reader: PartReader) -> None:
        self._part_reader = part_reader

    async def run(
        self, data: ReadAllPartCommand, current_employee: Employee
    ) -> PaginatedPartResponse:
        parts, total = await self._part_reader.read_all_active(data.limit, data.offset)
        return PaginatedPartResponse(
            items=[ReadPartResponse.model_validate(p) for p in parts],
            total=total,
            limit=data.limit,
            offset=data.offset,
        )
