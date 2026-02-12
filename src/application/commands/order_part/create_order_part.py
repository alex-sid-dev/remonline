from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_part_reader import OrderPartReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.order_parts.services import OrderPartService
from src.entities.orders.models import OrderUUID
from src.entities.parts.models import PartUUID
from src.entities.employees.models import Employee
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("create_order_part").bind(service="order_part")

@dataclass
class CreateOrderPartCommand:
    order_uuid: UUID
    part_uuid: UUID
    qty: int
    price: Optional[float] = None

class CreateOrderPartCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            entity_saver: EntitySaver,
            order_part_service: OrderPartService,
            order_part_reader: OrderPartReader,
            order_reader: OrderReader,
            part_reader: PartReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._order_part_reader = order_part_reader
        self._order_part_service = order_part_service
        self._order_reader = order_reader
        self._part_reader = part_reader

    async def run(self, data: CreateOrderPartCommand, current_employee: Employee) -> None:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.order_uuid))
        if not order:
            raise EntityNotFoundError(f"Order with uuid {data.order_uuid} not found")

        part = await self._part_reader.read_by_uuid(PartUUID(data.part_uuid))
        if not part:
            raise EntityNotFoundError(f"Part with uuid {data.part_uuid} not found")

        order_part = self._order_part_service.create_order_part(
            order_id=order.id,
            part_id=part.id,
            qty=data.qty,
            price=data.price
        )
        self._entity_saver.add_one(order_part)
        await self._transaction.commit()
        logger.info("Order part created successfully", order_part_uuid=str(order_part.uuid))
