from dataclasses import dataclass
from typing import Generic, TypeVar

OIDType = TypeVar("OIDType")
OUUIDType = TypeVar("OUUIDType")


@dataclass
class BaseEntity(Generic[OIDType, OUUIDType]):
    oid: OIDType
    ouuid: OUUIDType
