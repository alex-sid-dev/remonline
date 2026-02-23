from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.brand_reader import BrandReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.brands.models import BrandUUID
from src.entities.brands.services import BrandService
from src.entities.employees.models import Employee
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("update_brand").bind(service="brand")


@dataclass
class UpdateBrandCommand:
    uuid: UUID
    name: Optional[str] = None
    is_active: Optional[bool] = None


class UpdateBrandCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        brand_reader: BrandReader,
        brand_service: BrandService,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._brand_reader = brand_reader
        self._brand_service = brand_service

    async def run(self, data: UpdateBrandCommand, current_employee: Employee) -> None:
        brand = await self._brand_reader.read_by_uuid(BrandUUID(data.uuid))
        if not brand:
            raise EntityNotFoundError(message=f"Brand {data.uuid} not found")
        self._brand_service.update_brand(brand, name=data.name, is_active=data.is_active)
        self._entity_saver.add_one(brand)
        await self._transaction.commit()
        logger.info("Brand updated", brand_uuid=str(data.uuid))
