from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.part_reader import PartReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.parts.services import PartService

logger = structlog.get_logger("create_part").bind(service="part")


@dataclass
class CreatePartCommandResponse:
    uuid: UUID


@dataclass
class CreatePartCommand:
    name: str
    sku: str | None = None
    price: float | None = None
    stock_qty: int | None = None


class CreatePartCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        part_service: PartService,
        part_reader: PartReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._part_reader = part_reader
        self._part_service = part_service

    async def run(self, data: CreatePartCommand) -> CreatePartCommandResponse:
        part = self._part_service.create_part(
            name=data.name, sku=data.sku, price=data.price, stock_qty=data.stock_qty
        )
        self._entity_saver.add_one(part)
        await self._transaction.commit()
        logger.info("Part created successfully", part_uuid=str(part.uuid))
        return CreatePartCommandResponse(uuid=part.uuid)
