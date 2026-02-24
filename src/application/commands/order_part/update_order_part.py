from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.errors.part import PartStockNotEnoughError
from src.application.ports.order_part_reader import OrderPartReader
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import Transaction
from src.entities.employees.models import Employee
from src.entities.order_parts.models import OrderPartUUID
from src.entities.order_parts.services import OrderPartService

logger = structlog.get_logger("update_order_part").bind(service="order_part")


@dataclass
class UpdateOrderPartCommand:
    uuid: UUID
    qty: int | None = None
    price: float | None = None


class UpdateOrderPartCommandHandler(BaseCommandHandler):
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
        order_part = await self._order_part_reader.read_by_uuid(OrderPartUUID(data.uuid))
        if not order_part:
            raise EntityNotFoundError(f"OrderPart with uuid {data.uuid} not found")

        # Если меняется количество, синхронизируем остаток запчасти на складе.
        if data.qty is not None:
            from src.entities.parts.models import (  # локальный импорт, чтобы избежать циклов
                PartID,
            )

            part = await self._part_reader.read_by_id(PartID(order_part.part_id))  # type: ignore[arg-type]
            if part and part.stock_qty is not None:
                delta = data.qty - order_part.qty
                if data.qty <= 0:
                    raise PartStockNotEnoughError(
                        message="Количество запчасти в заказе должно быть положительным"
                    )

                current_stock = part.stock_qty or 0
                # delta > 0 означает, что мы хотим ДОБАВИТЬ ещё запчастей в заказ.
                if delta > 0 and current_stock < delta:
                    raise PartStockNotEnoughError(
                        message=f"Недостаточно запчастей на складе. Доступно: {current_stock}, требуется дополнительно: {delta}",
                    )

                part.stock_qty = current_stock - delta

        self._order_part_service.update_order_part(
            order_part=order_part,
            qty=data.qty,
            price=data.price,
        )
        await self._transaction.commit()
        logger.info("Order part updated successfully", order_part_uuid=str(data.uuid))
