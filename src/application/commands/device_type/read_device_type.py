from dataclasses import dataclass
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.device_type_reader import DeviceTypeReader
from src.entities.device_types.models import DeviceTypeUUID
from src.entities.employees.models import Employee
from src.application.commands.device_type.read_all_device_type import ReadDeviceTypeResponse
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("read_device_type").bind(service="device_type")

@dataclass
class ReadDeviceTypeCommand:
    uuid: UUID

class ReadDeviceTypeCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            device_type_reader: DeviceTypeReader,
    ) -> None:
        self._device_type_reader = device_type_reader

    async def run(self, data: ReadDeviceTypeCommand, current_employee: Employee) -> ReadDeviceTypeResponse:
        device_type = await self._device_type_reader.read_by_uuid(DeviceTypeUUID(data.uuid))
        if not device_type:
            raise EntityNotFoundError(f"DeviceType with uuid {data.uuid} not found")
            
        return ReadDeviceTypeResponse.from_entity(device_type)
