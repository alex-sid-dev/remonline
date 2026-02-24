from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.brand_reader import BrandReader
from src.application.ports.client_reader import ClientReader
from src.application.ports.device_reader import DeviceReader
from src.application.ports.device_type_reader import DeviceTypeReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.brands.models import BrandUUID
from src.entities.clients.models import ClientUUID
from src.entities.device_types.models import DeviceTypeUUID
from src.entities.devices.services import DeviceService

logger = structlog.get_logger("create_device").bind(service="device")


@dataclass
class CreateDeviceCommandResponse:
    uuid: UUID


@dataclass
class CreateDeviceCommand:
    client_uuid: UUID
    type_uuid: UUID
    brand_uuid: UUID
    model: str
    serial_number: str | None = None
    description: str | None = None


class CreateDeviceCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        device_service: DeviceService,
        device_reader: DeviceReader,
        client_reader: ClientReader,
        device_type_reader: DeviceTypeReader,
        brand_reader: BrandReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._device_reader = device_reader
        self._device_service = device_service
        self._client_reader = client_reader
        self._device_type_reader = device_type_reader
        self._brand_reader = brand_reader

    async def run(self, data: CreateDeviceCommand) -> CreateDeviceCommandResponse:
        client = await self._client_reader.read_by_uuid(ClientUUID(data.client_uuid))
        if not client:
            raise EntityNotFoundError(message=f"Client with uuid {data.client_uuid} not found")

        device_type = await self._device_type_reader.read_by_uuid(DeviceTypeUUID(data.type_uuid))
        if not device_type:
            raise EntityNotFoundError(message=f"Device type with uuid {data.type_uuid} not found")

        brand = await self._brand_reader.read_by_uuid(BrandUUID(data.brand_uuid))
        if not brand:
            raise EntityNotFoundError(message=f"Brand with uuid {data.brand_uuid} not found")

        device = self._device_service.create_device(
            client_id=client.id,
            type_id=device_type.id,
            brand_id=brand.id,
            model=data.model,
            serial_number=data.serial_number,
            description=data.description,
        )
        self._entity_saver.add_one(device)
        await self._transaction.commit()
        logger.info("Device created successfully", device_uuid=str(device.uuid))
        return CreateDeviceCommandResponse(
            uuid=device.uuid,
        )
