from dataclasses import dataclass
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.orders.models import OrderUUID
from src.entities.employees.models import Employee
from src.application.errors._base import EntityNotFoundError

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
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._order_reader = order_reader

    async def run(self, data: DeleteOrderCommand, current_employee: Employee) -> None:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.uuid))
        if not order:
            raise EntityNotFoundError(f"Order with uuid {data.uuid} not found")
            
        await self._entity_saver.delete(order)
        await self._transaction.commit()
        logger.info("Order deleted successfully", order_uuid=str(data.uuid))
