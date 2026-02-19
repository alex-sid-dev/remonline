from dataclasses import dataclass
from typing import List, Optional
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.device_reader import DeviceReader
from src.entities.devices.models import Device
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_device").bind(service="device")

@dataclass
class ReadAllDeviceCommand:
    pass

@dataclass
class ReadDeviceResponse:
    uuid: str
    client_id: int
    type_id: int
    brand: str
    model: str
    serial_number: Optional[str]
    description: Optional[str]

    @classmethod
    def from_entity(cls, entity: Device) -> "ReadDeviceResponse":
        return cls(
            uuid=str(entity.uuid),
            client_id=entity.client_id,
            type_id=entity.type_id,
            brand=entity.brand,
            model=entity.model,
            serial_number=entity.serial_number,
            description=entity.description
        )

class ReadAllDeviceCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            device_reader: DeviceReader,
    ) -> None:
        self._device_reader = device_reader

    async def run(self, data: ReadAllDeviceCommand, current_employee: Employee) -> List[ReadDeviceResponse]:
        devices = await self._device_reader.read_all_active()
        return [ReadDeviceResponse.from_entity(d) for d in devices]
