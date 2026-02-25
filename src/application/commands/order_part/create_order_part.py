from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands._stock_helpers import decrease_stock
from src.application.ports.order_part_reader import OrderPartReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.order_parts.services import OrderPartService
from src.entities.orders.models import OrderUUID
from src.entities.parts.models import PartUUID

logger = structlog.get_logger("create_order_part").bind(service="order_part")


@dataclass(frozen=True, slots=True)
class CreateOrderPartCommandResponse:
    uuid: UUID


@dataclass(frozen=True, slots=True)
class CreateOrderPartCommand:
    order_uuid: UUID
    part_uuid: UUID
    qty: int
    price: float | None = None


class CreateOrderPartCommandHandler:
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

    async def run(self, data: CreateOrderPartCommand) -> CreateOrderPartCommandResponse:
        order = await ensure_exists(
            self._order_reader.read_by_uuid,
            OrderUUID(data.order_uuid),
            f"Order with uuid {data.order_uuid}",
        )
        part = await ensure_exists(
            self._part_reader.read_by_uuid,
            PartUUID(data.part_uuid),
            f"Part with uuid {data.part_uuid}",
        )

        decrease_stock(part, data.qty)

        existing = await self._order_part_reader.read_by_order_and_part(order.id, part.id)

        if existing:
            self._order_part_service.update_order_part(
                order_part=existing,
                qty=existing.qty + data.qty,
                price=data.price if data.price is not None else existing.price,
            )
            order_part = existing
        else:
            order_part = self._order_part_service.create_order_part(
                order_id=order.id,
                part_id=part.id,
                qty=data.qty,
                price=data.price,
            )
            self._entity_saver.add_one(order_part)
        await self._transaction.commit()
        logger.info("Order part created successfully", order_part_uuid=str(order_part.uuid))
        return CreateOrderPartCommandResponse(
            uuid=order_part.uuid,
        )
