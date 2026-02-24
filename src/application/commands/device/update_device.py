from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.brand_reader import BrandReader
from src.application.ports.device_reader import DeviceReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.brands.models import BrandUUID
from src.entities.devices.models import DeviceUUID
from src.entities.devices.services import DeviceService
from src.entities.employees.models import Employee

logger = structlog.get_logger("update_device").bind(service="device")


@dataclass
class UpdateDeviceCommand:
    uuid: UUID
    brand_uuid: UUID | None = None
    model: str | None = None
    serial_number: str | None = None
    is_active: bool | None = None


class UpdateDeviceCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        device_reader: DeviceReader,
        brand_reader: BrandReader,
        device_service: DeviceService,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._device_reader = device_reader
        self._brand_reader = brand_reader
        self._device_service = device_service

    async def run(self, data: UpdateDeviceCommand, current_employee: Employee) -> None:
        device = await self._device_reader.read_by_uuid(DeviceUUID(data.uuid))
        if not device:
            raise EntityNotFoundError(message=f"Device with uuid {data.uuid} not found")

        brand_id = None
        if data.brand_uuid is not None:
            brand = await self._brand_reader.read_by_uuid(BrandUUID(data.brand_uuid))
            if not brand:
                raise EntityNotFoundError(message=f"Brand with uuid {data.brand_uuid} not found")
            brand_id = brand.id

        self._device_service.update_device(
            device=device,
            brand_id=brand_id,
            model=data.model,
            serial_number=data.serial_number,
            is_active=data.is_active,
        )
        self._entity_saver.add_one(device)
        await self._transaction.commit()
        logger.info("Device updated successfully", device_uuid=str(data.uuid))
