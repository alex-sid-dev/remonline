from typing import List, Optional, Protocol
from src.entities.devices.models import Device, DeviceID, DeviceUUID
from src.entities.clients.models import ClientID

class DeviceReader(Protocol):
    async def read_by_id(self, device_id: DeviceID) -> Optional[Device]:
        ...

    async def read_by_uuid(self, device_uuid: DeviceUUID) -> Optional[Device]:
        ...

    async def read_all_active(self) -> List[Device]:
        ...

    async def read_by_client_id(self, client_id: ClientID) -> List[Device]:
        ...
