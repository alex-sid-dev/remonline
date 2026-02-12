from dataclasses import dataclass
from typing import Optional, NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity

PartID = NewType("PartID", int)
PartUUID = NewType("PartUUID", UUID)


@dataclass
class Part(BaseEntity[PartID, PartUUID]):
    name: str
    sku: Optional[str] = None
    price: Optional[float] = None
    stock_qty: Optional[int] = None
    is_active: bool = True
