from uuid import UUID

import structlog
from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import ConflictError, EntityNotFoundError
from src.application.ports.brand_reader import BrandReader
from src.application.ports.device_reader import DeviceReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.brands.models import BrandUUID
from src.entities.employees.models import Employee

logger = structlog.get_logger("delete_brand").bind(service="brand")


class DeleteBrandCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        brand_reader: BrandReader,
        device_reader: DeviceReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._brand_reader = brand_reader
        self._device_reader = device_reader

    async def run(self, uuid: UUID, current_employee: Employee) -> None:
        brand = await self._brand_reader.read_by_uuid(BrandUUID(uuid))
        if not brand:
            raise EntityNotFoundError(message=f"Brand {uuid} not found")
        devices = await self._device_reader.read_all_active()
        if any(getattr(d, "brand_id", None) == brand.id for d in devices):
            raise ConflictError(message="Нельзя удалить бренд: есть устройства с этим брендом")
        await self._entity_saver.delete(brand)
        await self._transaction.commit()
        logger.info("Brand deleted", brand_uuid=str(uuid))
