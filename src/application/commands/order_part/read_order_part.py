from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.commands.order_part.read_all_order_part import ReadOrderPartResponse
from src.application.errors._base import EntityNotFoundError
from src.application.ports.order_part_reader import OrderPartReader
from src.entities.employees.models import Employee
from src.entities.order_parts.models import OrderPartUUID

logger = structlog.get_logger("read_order_part").bind(service="order_part")


@dataclass
class ReadOrderPartCommand:
    uuid: UUID


class ReadOrderPartCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        order_part_reader: OrderPartReader,
    ) -> None:
        self._order_part_reader = order_part_reader

    async def run(
        self, data: ReadOrderPartCommand, current_employee: Employee
    ) -> ReadOrderPartResponse:
        order_part = await self._order_part_reader.read_by_uuid(OrderPartUUID(data.uuid))
        if not order_part:
            raise EntityNotFoundError(f"OrderPart with uuid {data.uuid} not found")

        return ReadOrderPartResponse(
            uuid=order_part.uuid,
            order_id=order_part.order_id,
            part_id=order_part.part_id,
            qty=order_part.qty,
            price=order_part.price,
        )
