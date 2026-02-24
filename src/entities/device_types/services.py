from uuid import uuid4

from src.entities.device_types.models import DeviceType, DeviceTypeUUID


class DeviceTypeService:
    def create_device_type(
        self,
        name: str,
        description: str = "",
    ) -> DeviceType:
        return DeviceType(
            id=None,  # type: ignore
            uuid=DeviceTypeUUID(uuid4()),
            name=name,
            description=description,
            is_active=True,
        )

    def update_device_type(
        self,
        device_type: DeviceType,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> DeviceType:
        if name is not None:
            device_type.name = name
        if description is not None:
            device_type.description = description
        if is_active is not None:
            device_type.is_active = is_active
        return device_type
