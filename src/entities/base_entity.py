from dataclasses import dataclass
from typing import Generic, TypeVar

IDType = TypeVar("IDType")
UUIDType = TypeVar("UUIDType")


@dataclass
class BaseEntity(Generic[IDType, UUIDType]):
    id: IDType
    uuid: UUIDType
