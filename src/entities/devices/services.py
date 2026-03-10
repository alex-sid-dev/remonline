from uuid import uuid4

from src.entities.brands.models import BrandID
from src.entities.clients.models import ClientID
from src.entities.device_types.models import DeviceTypeID
from src.entities.devices.models import Device, DeviceUUID
from src.entities.organizations.models import OrganizationID


class DeviceService:
    def create_device(
        self,
        client_id: ClientID,
        type_id: DeviceTypeID,
        brand_id: BrandID,
        model: str,
        serial_number: str | None = None,
        description: str | None = None,
        organization_id: OrganizationID = OrganizationID(1),
    ) -> Device:
        return Device(
            id=None,  # type: ignore
            uuid=DeviceUUID(uuid4()),
            client_id=client_id,
            type_id=type_id,
            brand_id=brand_id,
            organization_id=organization_id,
            model=model,
            serial_number=serial_number,
            description=description,
            is_active=True,
        )

    def update_device(
        self,
        device: Device,
        brand_id: BrandID | None = None,
        model: str | None = None,
        serial_number: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> Device:
        if brand_id is not None:
            device.brand_id = brand_id
        if model is not None:
            device.model = model
        if serial_number is not None:
            device.serial_number = serial_number
        if description is not None:
            device.description = description
        if is_active is not None:
            device.is_active = is_active
        return device
