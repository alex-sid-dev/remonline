from dataclasses import dataclass
from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict

from src.application.ports.device_type_reader import DeviceTypeReader
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_device_type").bind(service="device_type")


@dataclass(frozen=True, slots=True)
class ReadAllDeviceTypeCommand:
    pass


class ReadDeviceTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    description: str


class ReadAllDeviceTypeCommandHandler:
    def __init__(
        self,
        device_type_reader: DeviceTypeReader,
    ) -> None:
        self._device_type_reader = device_type_reader

    async def run(
        self, data: ReadAllDeviceTypeCommand, current_employee: Employee
    ) -> list[ReadDeviceTypeResponse]:
        device_types = await self._device_type_reader.read_all_active()
        return [ReadDeviceTypeResponse.model_validate(dt) for dt in device_types]
