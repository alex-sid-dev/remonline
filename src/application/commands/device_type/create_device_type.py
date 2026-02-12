from dataclasses import dataclass
from typing import Optional
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.device_type_reader import DeviceTypeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.device_types.services import DeviceTypeService
from src.entities.employees.models import Employee

logger = structlog.get_logger("create_device_type").bind(service="device_type")

@dataclass
class CreateDeviceTypeCommand:
    name: str
    description: str = ""

class CreateDeviceTypeCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            entity_saver: EntitySaver,
            device_type_service: DeviceTypeService,
            device_type_reader: DeviceTypeReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._device_type_reader = device_type_reader
        self._device_type_service = device_type_service

    async def run(self, data: CreateDeviceTypeCommand, current_employee: Employee) -> None:
        device_type = self._device_type_service.create_device_type(
            name=data.name,
            description=data.description
        )
        self._entity_saver.add_one(device_type)
        await self._transaction.commit()
        logger.info("Device type created successfully", device_type_uuid=str(device_type.uuid))
