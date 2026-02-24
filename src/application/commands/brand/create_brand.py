from dataclasses import dataclass
from uuid import UUID

import structlog
from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.brands.services import BrandService

logger = structlog.get_logger("create_brand").bind(service="brand")


@dataclass
class CreateBrandCommand:
    name: str


@dataclass
class CreateBrandCommandResponse:
    uuid: UUID


class CreateBrandCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        brand_service: BrandService,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._brand_service = brand_service

    async def run(self, data: CreateBrandCommand) -> CreateBrandCommandResponse:
        brand = self._brand_service.create_brand(name=data.name)
        self._entity_saver.add_one(brand)
        await self._transaction.commit()
        logger.info("Brand created", brand_uuid=str(brand.uuid))
        return CreateBrandCommandResponse(uuid=brand.uuid)
