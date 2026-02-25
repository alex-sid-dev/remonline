from dataclasses import dataclass
from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict

from src.application.ports.order_part_reader import OrderPartReader
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_order_part").bind(service="order_part")


class ReadOrderPartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    order_id: int
    part_id: int
    qty: int
    price: float | None = None


@dataclass(frozen=True, slots=True)
class ReadAllOrderPartCommand:
    pass


class ReadAllOrderPartCommandHandler:
    def __init__(self, order_part_reader: OrderPartReader) -> None:
        self._order_part_reader = order_part_reader

    async def run(
        self, data: ReadAllOrderPartCommand, current_employee: Employee
    ) -> list[ReadOrderPartResponse]:
        order_parts = await self._order_part_reader.read_all()
        return [ReadOrderPartResponse.model_validate(op) for op in order_parts]
