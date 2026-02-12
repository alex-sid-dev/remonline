from dataclasses import dataclass
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.device_reader import DeviceReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.devices.models import DeviceUUID
from src.entities.employees.models import Employee
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("delete_device").bind(service="device")

@dataclass
class DeleteDeviceCommand:
    uuid: UUID

class DeleteDeviceCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            entity_saver: EntitySaver,
            device_reader: DeviceReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._device_reader = device_reader

    async def run(self, data: DeleteDeviceCommand, current_employee: Employee) -> None:
        device = await self._device_reader.read_by_uuid(DeviceUUID(data.uuid))
        if not device:
            raise EntityNotFoundError(f"Device with uuid {data.uuid} not found")
            
        await self._entity_saver.delete(device)
        await self._transaction.commit()
        logger.info("Device deleted successfully", device_uuid=str(data.uuid))
