from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.ports.device_type_reader import DeviceTypeReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.device_types.models import DeviceTypeUUID
from src.entities.employees.models import Employee

logger = structlog.get_logger("delete_device_type").bind(service="device_type")


@dataclass(frozen=True, slots=True)
class DeleteDeviceTypeCommand:
    uuid: UUID


class DeleteDeviceTypeCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        device_type_reader: DeviceTypeReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._device_type_reader = device_type_reader

    async def run(self, data: DeleteDeviceTypeCommand, current_employee: Employee) -> None:
        device_type = await ensure_exists(
            self._device_type_reader.read_by_uuid,
            DeviceTypeUUID(data.uuid),
            f"DeviceType with uuid {data.uuid}",
        )

        await self._entity_saver.delete(device_type)
        await self._transaction.commit()
        logger.info("DeviceType deleted successfully", device_type_uuid=str(data.uuid))
