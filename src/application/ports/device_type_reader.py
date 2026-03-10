from typing import Protocol

from src.entities.device_types.models import DeviceType, DeviceTypeID, DeviceTypeUUID


class DeviceTypeReader(Protocol):
    async def read_by_id(self, device_type_id: DeviceTypeID) -> DeviceType | None: ...

    async def read_by_uuid(self, device_type_uuid: DeviceTypeUUID) -> DeviceType | None: ...

    async def read_all_active(self, organization_id: int) -> list[DeviceType]: ...
