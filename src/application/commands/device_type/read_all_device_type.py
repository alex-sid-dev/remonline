from dataclasses import dataclass
from typing import List, Optional
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.device_type_reader import DeviceTypeReader
from src.entities.device_types.models import DeviceType
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_device_type").bind(service="device_type")

@dataclass
class ReadAllDeviceTypeCommand:
    pass

@dataclass
class ReadDeviceTypeResponse:
    id: int
    uuid: str
    name: str
    description: str

    @classmethod
    def from_entity(cls, entity: DeviceType) -> "ReadDeviceTypeResponse":
        return cls(
            id=entity.id,
            uuid=str(entity.uuid),
            name=entity.name,
            description=entity.description
        )

class ReadAllDeviceTypeCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            device_type_reader: DeviceTypeReader,
    ) -> None:
        self._device_type_reader = device_type_reader

    async def run(self, data: ReadAllDeviceTypeCommand, current_employee: Employee) -> List[ReadDeviceTypeResponse]:
        device_types = await self._device_type_reader.read_all_active()
        return [ReadDeviceTypeResponse.from_entity(dt) for dt in device_types]
