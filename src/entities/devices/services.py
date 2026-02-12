from typing import Optional
from uuid import uuid4
from src.entities.devices.models import Device, DeviceID, DeviceUUID
from src.entities.clients.models import ClientID
from src.entities.device_types.models import DeviceTypeID

class DeviceService:
    def create_device(
        self,
        client_id: ClientID,
        type_id: DeviceTypeID,
        brand: str,
        model: str,
        serial_number: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Device:
        return Device(
            id=None,  # type: ignore
            uuid=DeviceUUID(uuid4()),
            client_id=client_id,
            type_id=type_id,
            brand=brand,
            model=model,
            serial_number=serial_number,
            description=description,
            is_active=True,
        )

    def update_device(
        self,
        device: Device,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        serial_number: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Device:
        if brand is not None:
            device.brand = brand
        if model is not None:
            device.model = model
        if serial_number is not None:
            device.serial_number = serial_number
        if description is not None:
            device.description = description
        if is_active is not None:
            device.is_active = is_active
        return device
