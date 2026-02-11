from dataclasses import dataclass
from typing import Optional, NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.clients.models import ClientID
from src.entities.device_types.models import DeviceTypeID

DeviceID = NewType("DeviceID", int)
DeviceUUID = NewType("DeviceUUID", UUID)


@dataclass
class Device(BaseEntity[DeviceID, DeviceUUID]):
    client_id: ClientID
    type_id: DeviceTypeID
    brand: str
    model: str
    serial_number: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True

    _type_name: Optional[str] = None

    @property
    def type_name(self) -> Optional[str]:
        if hasattr(self, "type") and self.type is not None:
            return self.type.name
        return self._type_name
