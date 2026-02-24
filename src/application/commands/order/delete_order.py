from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.order_reader import OrderReader
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee
from src.entities.orders.models import OrderUUID

logger = structlog.get_logger("delete_order").bind(service="order")


@dataclass
class DeleteOrderCommand:
    uuid: UUID


class DeleteOrderCommandHandler(BaseCommandHandler):
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
        order = await self._order_reader.read_by_uuid(OrderUUID(data.uuid))
        if not order:
            raise EntityNotFoundError(f"Order with uuid {data.uuid} not found")

        # Сохраняем связаное устройство, чтобы удалить его после удаления заказа.
        device = getattr(order, "device", None)

        # Вернуть на склад все запчасти, использованные в заказе.
        from src.entities.parts.models import PartID

        for order_part in getattr(order, "parts", []) or []:
            part = await self._part_reader.read_by_id(PartID(order_part.part_id))  # type: ignore[arg-type]
            if part and part.stock_qty is not None:
                part.stock_qty = (part.stock_qty or 0) + (order_part.qty or 0)

        # Удалить сам заказ (каскадом удалятся работы, платежи и привязки запчастей).
        await self._entity_saver.delete(order)

        # Удалить устройство, привязанное к заказу.
        if device is not None:
            await self._entity_saver.delete(device)

        await self._transaction.commit()
        logger.info("Order deleted successfully", order_uuid=str(data.uuid))
