from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.order_part_reader import OrderPartReader
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee
from src.entities.order_parts.models import OrderPartUUID

logger = structlog.get_logger("delete_order_part").bind(service="order_part")


@dataclass
class DeleteOrderPartCommand:
    uuid: UUID


class DeleteOrderPartCommandHandler(BaseCommandHandler):
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
        order_part = await self._order_part_reader.read_by_uuid(OrderPartUUID(data.uuid))
        if not order_part:
            raise EntityNotFoundError(f"OrderPart with uuid {data.uuid} not found")

        # Возвращаем остаток на склад (если он ведётся).
        from src.entities.parts.models import PartID

        part = await self._part_reader.read_by_id(PartID(order_part.part_id))  # type: ignore[arg-type]
        if part and part.stock_qty is not None:
            part.stock_qty = (part.stock_qty or 0) + order_part.qty

        await self._entity_saver.delete(order_part)
        await self._transaction.commit()
        logger.info("OrderPart deleted successfully", order_part_uuid=str(data.uuid))
