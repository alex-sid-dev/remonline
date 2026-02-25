from typing import Protocol

from src.entities.brands.models import BrandID
from src.entities.clients.models import ClientID
from src.entities.devices.models import Device, DeviceID, DeviceUUID


class DeviceReader(Protocol):
    async def read_by_id(self, device_id: DeviceID) -> Device | None: ...

    async def read_by_uuid(self, device_uuid: DeviceUUID) -> Device | None: ...

    async def read_all_active(self) -> list[Device]: ...

    async def read_by_client_id(self, client_id: ClientID) -> list[Device]: ...

    async def exists_by_brand_id(self, brand_id: BrandID) -> bool: ...
