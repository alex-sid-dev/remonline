from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands.order_part.read_all_order_part import ReadOrderPartResponse
from src.application.ports.order_part_reader import OrderPartReader
from src.entities.employees.models import Employee
from src.entities.order_parts.models import OrderPartUUID

logger = structlog.get_logger("read_order_part").bind(service="order_part")


@dataclass(frozen=True, slots=True)
class ReadOrderPartCommand:
    uuid: UUID


class ReadOrderPartCommandHandler:
    def __init__(
        self,
        order_part_reader: OrderPartReader,
    ) -> None:
        self._order_part_reader = order_part_reader

    async def run(
        self, data: ReadOrderPartCommand, current_employee: Employee
    ) -> ReadOrderPartResponse:
        order_part = await ensure_exists(
            self._order_part_reader.read_by_uuid,
            OrderPartUUID(data.uuid),
            f"OrderPart with uuid {data.uuid}",
        )
        return ReadOrderPartResponse.model_validate(order_part)
