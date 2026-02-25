from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.ports.device_type_reader import DeviceTypeReader
from src.application.ports.transaction import Transaction
from src.entities.device_types.models import DeviceTypeUUID
from src.entities.device_types.services import DeviceTypeService
from src.entities.employees.models import Employee

logger = structlog.get_logger("update_device_type").bind(service="device_type")


@dataclass(frozen=True, slots=True)
class UpdateDeviceTypeCommand:
    uuid: UUID
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class UpdateDeviceTypeCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        device_type_reader: DeviceTypeReader,
        device_type_service: DeviceTypeService,
    ) -> None:
        self._transaction = transaction
        self._device_type_reader = device_type_reader
        self._device_type_service = device_type_service

    async def run(self, data: UpdateDeviceTypeCommand, current_employee: Employee) -> None:
        device_type = await ensure_exists(
            self._device_type_reader.read_by_uuid, DeviceTypeUUID(data.uuid),
            f"Device type with uuid {data.uuid}",
        )

        self._device_type_service.update_device_type(
            device_type=device_type,
            name=data.name,
            description=data.description,
            is_active=data.is_active,
        )
        await self._transaction.commit()
        logger.info("Device type updated successfully", device_type_uuid=str(data.uuid))
