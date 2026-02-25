from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands._stock_helpers import increase_stock
from src.application.ports.order_part_reader import OrderPartReader
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee
from src.entities.order_parts.models import OrderPartUUID
from src.entities.parts.models import PartID

logger = structlog.get_logger("delete_order_part").bind(service="order_part")


@dataclass(frozen=True, slots=True)
class DeleteOrderPartCommand:
    uuid: UUID


class DeleteOrderPartCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        order_part_reader: OrderPartReader,
        part_reader: PartReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._order_part_reader = order_part_reader
        self._part_reader = part_reader

    async def run(self, data: DeleteOrderPartCommand, current_employee: Employee) -> None:
        order_part = await ensure_exists(
            self._order_part_reader.read_by_uuid,
            OrderPartUUID(data.uuid),
            f"OrderPart with uuid {data.uuid}",
        )

        part = await self._part_reader.read_by_id(PartID(order_part.part_id))  # type: ignore[arg-type]
        if part:
            increase_stock(part, order_part.qty)

        await self._entity_saver.delete(order_part)
        await self._transaction.commit()
        logger.info("OrderPart deleted successfully", order_part_uuid=str(data.uuid))
