from dataclasses import dataclass
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.entities.orders.models import OrderUUID
from src.entities.employees.models import Employee
from src.application.commands.order.read_all_order import ReadOrderResponse
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("read_order").bind(service="order")

@dataclass
class ReadOrderCommand:
    uuid: UUID

class ReadOrderCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            order_reader: OrderReader,
    ) -> None:
        self._order_reader = order_reader

    async def run(self, data: ReadOrderCommand, current_employee: Employee) -> ReadOrderResponse:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.uuid))
        if not order:
            raise EntityNotFoundError(f"Order with uuid {data.uuid} not found")
            
        return ReadOrderResponse.from_entity(order)
