from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands.device_type.read_all_device_type import ReadDeviceTypeResponse
from src.application.ports.device_type_reader import DeviceTypeReader
from src.entities.device_types.models import DeviceTypeUUID
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_device_type").bind(service="device_type")


@dataclass(frozen=True, slots=True)
class ReadDeviceTypeCommand:
    uuid: UUID


class ReadDeviceTypeCommandHandler:
    def __init__(
        self,
        device_type_reader: DeviceTypeReader,
    ) -> None:
        self._device_type_reader = device_type_reader

    async def run(
        self, data: ReadDeviceTypeCommand, current_employee: Employee
    ) -> ReadDeviceTypeResponse:
        device_type = await ensure_exists(
            self._device_type_reader.read_by_uuid, DeviceTypeUUID(data.uuid),
            f"DeviceType with uuid {data.uuid}",
        )
        return ReadDeviceTypeResponse.model_validate(device_type)
