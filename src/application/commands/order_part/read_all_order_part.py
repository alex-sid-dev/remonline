from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_part_reader import OrderPartReader
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_order_part").bind(service="order_part")


@dataclass
class ReadOrderPartResponse:
    uuid: UUID
    order_id: int
    part_id: int
    qty: int
    price: float | None


@dataclass
class ReadAllOrderPartCommand:
    pass


class ReadAllOrderPartCommandHandler(BaseCommandHandler):
    def __init__(self, order_part_reader: OrderPartReader) -> None:
        self._order_part_reader = order_part_reader

    async def run(
        self, data: ReadAllOrderPartCommand, current_employee: Employee
    ) -> list[ReadOrderPartResponse]:
        order_parts = await self._order_part_reader.read_all()
        return [
            ReadOrderPartResponse(
                uuid=op.uuid, order_id=op.order_id, part_id=op.part_id, qty=op.qty, price=op.price
            )
            for op in order_parts
        ]
