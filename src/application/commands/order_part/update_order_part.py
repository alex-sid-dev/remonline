from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_part_reader import OrderPartReader
from src.application.ports.transaction import Transaction
from src.entities.order_parts.services import OrderPartService
from src.entities.order_parts.models import OrderPartUUID
from src.entities.employees.models import Employee
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("update_order_part").bind(service="order_part")

@dataclass
class UpdateOrderPartCommand:
    uuid: UUID
    qty: Optional[int] = None
    price: Optional[float] = None

class UpdateOrderPartCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            order_part_service: OrderPartService,
            order_part_reader: OrderPartReader,
    ) -> None:
        self._transaction = transaction
        self._order_part_reader = order_part_reader
        self._order_part_service = order_part_service

    async def run(self, data: UpdateOrderPartCommand, current_employee: Employee) -> None:
        order_part = await self._order_part_reader.read_by_uuid(OrderPartUUID(data.uuid))
        if not order_part:
            raise EntityNotFoundError(f"OrderPart with uuid {data.uuid} not found")

        self._order_part_service.update_order_part(
            order_part=order_part,
            qty=data.qty,
            price=data.price
        )
        await self._transaction.commit()
        logger.info("Order part updated successfully", order_part_uuid=str(data.uuid))
