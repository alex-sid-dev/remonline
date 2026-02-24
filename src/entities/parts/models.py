from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity

PartID = NewType("PartID", int)
PartUUID = NewType("PartUUID", UUID)


@dataclass
class Part(BaseEntity[PartID, PartUUID]):
    name: str
    sku: str | None = None
    price: float | None = None
    stock_qty: int | None = None
    is_active: bool = True
