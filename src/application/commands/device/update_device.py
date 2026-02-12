from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.device_reader import DeviceReader
from src.application.ports.transaction import Transaction
from src.entities.devices.models import DeviceUUID
from src.entities.devices.services import DeviceService
from src.entities.employees.models import Employee
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("update_device").bind(service="device")

@dataclass
class UpdateDeviceCommand:
    uuid: UUID
    model: Optional[str] = None
    serial_number: Optional[str] = None
    is_active: Optional[bool] = None

class UpdateDeviceCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            device_reader: DeviceReader,
            device_service: DeviceService,
    ) -> None:
        self._transaction = transaction
        self._device_reader = device_reader
        self._device_service = device_service

    async def run(self, data: UpdateDeviceCommand, current_employee: Employee) -> None:
        device = await self._device_reader.read_by_uuid(DeviceUUID(data.uuid))
        if not device:
            raise EntityNotFoundError(f"Device with uuid {data.uuid} not found")

        self._device_service.update_device(
            device=device,
            model=data.model,
            serial_number=data.serial_number,
            is_active=data.is_active
        )
        await self._transaction.commit()
        logger.info("Device updated successfully", device_uuid=str(data.uuid))
