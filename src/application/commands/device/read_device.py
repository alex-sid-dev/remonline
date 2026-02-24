from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.commands.device.read_all_device import ReadDeviceResponse
from src.application.errors._base import EntityNotFoundError
from src.application.ports.device_reader import DeviceReader
from src.entities.devices.models import DeviceUUID
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_device").bind(service="device")


@dataclass
class ReadDeviceCommand:
    uuid: UUID


class ReadDeviceCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        device_reader: DeviceReader,
    ) -> None:
        self._device_reader = device_reader

    async def run(self, data: ReadDeviceCommand, current_employee: Employee) -> ReadDeviceResponse:
        device = await self._device_reader.read_by_uuid(DeviceUUID(data.uuid))
        if not device:
            raise EntityNotFoundError(f"Device with uuid {data.uuid} not found")

        return ReadDeviceResponse.from_entity(device)
