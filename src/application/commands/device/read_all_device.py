from dataclasses import dataclass
from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict

from src.application.ports.device_reader import DeviceReader
from src.entities.devices.models import Device
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_device").bind(service="device")


@dataclass(frozen=True, slots=True)
class ReadAllDeviceCommand:
    pass


class ReadDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    client_id: int
    type_id: int
    brand_uuid: UUID | None = None
    brand: str = "—"
    model: str
    serial_number: str | None = None
    description: str | None = None

    @classmethod
    def from_entity(cls, entity: Device) -> "ReadDeviceResponse":
        brand_obj = getattr(entity, "brand", None)
        brand_name = brand_obj.name if brand_obj else "—"
        brand_uuid = brand_obj.uuid if brand_obj else None
        return cls(
            uuid=entity.uuid,
            client_id=entity.client_id,
            type_id=entity.type_id,
            brand_uuid=brand_uuid,
            brand=brand_name,
            model=entity.model,
            serial_number=entity.serial_number,
            description=entity.description,
        )


class ReadAllDeviceCommandHandler:
    def __init__(
        self,
        device_reader: DeviceReader,
    ) -> None:
        self._device_reader = device_reader

    async def run(
        self,
        data: ReadAllDeviceCommand,
        current_employee: Employee,
    ) -> list[ReadDeviceResponse]:
        devices = await self._device_reader.read_all_active(
            organization_id=current_employee.organization_id,
        )
        return [ReadDeviceResponse.from_entity(d) for d in devices]
