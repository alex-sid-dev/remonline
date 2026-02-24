from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.brands.models import BrandID
from src.entities.clients.models import ClientID
from src.entities.device_types.models import DeviceTypeID

DeviceID = NewType("DeviceID", int)
DeviceUUID = NewType("DeviceUUID", UUID)


@dataclass
class Device(BaseEntity[DeviceID, DeviceUUID]):
    client_id: ClientID
    type_id: DeviceTypeID
    brand_id: BrandID
    model: str
    serial_number: str | None = None
    description: str | None = None
    is_active: bool = True

    _type_name: str | None = None

    @property
    def type_name(self) -> str | None:
        if hasattr(self, "type") and self.type is not None:
            return self.type.name
        return self._type_name
