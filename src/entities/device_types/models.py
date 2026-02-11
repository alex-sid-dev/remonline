from dataclasses import dataclass
from typing import NewType
from uuid import UUID
from src.entities.base_entity import BaseEntity

DeviceTypeID = NewType("DeviceTypeID", int)
DeviceTypeUUID = NewType("DeviceTypeUUID", UUID)


@dataclass
class DeviceType(BaseEntity[DeviceTypeID, DeviceTypeUUID]):
    name: str
    description: str = ""
    is_active: bool = True
