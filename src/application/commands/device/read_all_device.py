from dataclasses import dataclass

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
    brand_uuid: str | None
    brand: str
    model: str
    serial_number: str | None
    description: str | None

    @classmethod
    def from_entity(cls, entity: Device) -> "ReadDeviceResponse":
        brand_obj = getattr(entity, "brand", None)
        brand_name = brand_obj.name if brand_obj else "—"
        brand_uuid = str(brand_obj.uuid) if brand_obj else None
        return cls(
            uuid=str(entity.uuid),
            client_id=entity.client_id,
            type_id=entity.type_id,
            brand_uuid=brand_uuid,
            brand=brand_name,
            model=entity.model,
            serial_number=entity.serial_number,
            description=entity.description,
        )


class ReadAllDeviceCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        device_reader: DeviceReader,
    ) -> None:
        self._device_reader = device_reader

    async def run(
        self, data: ReadAllDeviceCommand, current_employee: Employee
    ) -> list[ReadDeviceResponse]:
        devices = await self._device_reader.read_all_active()
        return [ReadDeviceResponse.from_entity(d) for d in devices]
