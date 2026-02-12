from typing import List, Optional, Protocol
from src.entities.device_types.models import DeviceType, DeviceTypeID, DeviceTypeUUID

class DeviceTypeReader(Protocol):
    async def read_by_id(self, device_type_id: DeviceTypeID) -> Optional[DeviceType]:
        ...

    async def read_by_uuid(self, device_type_uuid: DeviceTypeUUID) -> Optional[DeviceType]:
        ...

    async def read_all_active(self) -> List[DeviceType]:
        ...
