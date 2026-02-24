from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import Transaction
from src.entities.employees.models import Employee
from src.entities.parts.models import PartUUID
from src.entities.parts.services import PartService

logger = structlog.get_logger("update_part").bind(service="part")


@dataclass
class UpdatePartCommand:
    uuid: UUID
    name: str | None = None
    sku: str | None = None
    price: float | None = None
    stock_qty: int | None = None
    is_active: bool | None = None


class UpdatePartCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        part_reader: PartReader,
        part_service: PartService,
    ) -> None:
        self._transaction = transaction
        self._part_reader = part_reader
        self._part_service = part_service

    async def run(self, data: UpdatePartCommand, current_employee: Employee) -> None:
        part = await self._part_reader.read_by_uuid(PartUUID(data.uuid))
        if not part:
            raise EntityNotFoundError(f"Part with uuid {data.uuid} not found")

        self._part_service.update_part(
            part=part,
            name=data.name,
            sku=data.sku,
            price=data.price,
            stock_qty=data.stock_qty,
            is_active=data.is_active,
        )
        await self._transaction.commit()
        logger.info("Part updated successfully", part_uuid=str(data.uuid))
