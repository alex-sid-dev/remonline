from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands._stock_helpers import increase_stock
from src.application.ports.order_reader import OrderReader
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee
from src.entities.orders.models import OrderUUID
from src.entities.parts.models import PartID

logger = structlog.get_logger("delete_order").bind(service="order")


@dataclass(frozen=True, slots=True)
class DeleteOrderCommand:
    uuid: UUID


class DeleteOrderCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        order_reader: OrderReader,
        part_reader: PartReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._order_reader = order_reader
        self._part_reader = part_reader

    async def run(self, data: DeleteOrderCommand, current_employee: Employee) -> None:
        order = await ensure_exists(
            self._order_reader.read_by_uuid,
            OrderUUID(data.uuid),
            f"Order with uuid {data.uuid}",
        )

        device = getattr(order, "device", None)

        for order_part in getattr(order, "parts", []) or []:
            part = await self._part_reader.read_by_id(PartID(order_part.part_id))  # type: ignore[arg-type]
            if part:
                increase_stock(part, order_part.qty or 0)

        await self._entity_saver.delete(order)

        if device is not None:
            await self._entity_saver.delete(device)

        await self._transaction.commit()
        logger.info("Order deleted successfully", order_uuid=str(data.uuid))
