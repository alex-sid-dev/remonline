from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands._stock_helpers import adjust_stock_delta
from src.application.ports.order_part_reader import OrderPartReader
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import Transaction
from src.entities.employees.models import Employee
from src.entities.order_parts.models import OrderPartUUID
from src.entities.order_parts.services import OrderPartService
from src.entities.parts.models import PartID

logger = structlog.get_logger("update_order_part").bind(service="order_part")


@dataclass(frozen=True, slots=True)
class UpdateOrderPartCommand:
    uuid: UUID
    qty: int | None = None
    price: float | None = None


class UpdateOrderPartCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        order_part_service: OrderPartService,
        order_part_reader: OrderPartReader,
        part_reader: PartReader,
    ) -> None:
        self._transaction = transaction
        self._order_part_reader = order_part_reader
        self._order_part_service = order_part_service
        self._part_reader = part_reader

    async def run(self, data: UpdateOrderPartCommand, current_employee: Employee) -> None:
        order_part = await ensure_exists(
            self._order_part_reader.read_by_uuid, OrderPartUUID(data.uuid),
            f"OrderPart with uuid {data.uuid}",
        )

        if data.qty is not None:
            part = await self._part_reader.read_by_id(PartID(order_part.part_id))  # type: ignore[arg-type]
            if part:
                adjust_stock_delta(part, order_part.qty, data.qty)

        self._order_part_service.update_order_part(
            order_part=order_part,
            qty=data.qty,
            price=data.price,
        )
        await self._transaction.commit()
        logger.info("Order part updated successfully", order_part_uuid=str(data.uuid))
