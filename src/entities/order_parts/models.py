from dataclasses import dataclass
from typing import NewType, Optional
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.orders.models import OrderID
from src.entities.parts.models import PartID

OrderPartID = NewType("OrderPartID", int)
OrderPartUUID = NewType("OrderPartUUID", UUID)


@dataclass
class OrderPart(BaseEntity[OrderPartID, OrderPartUUID]):
    order_id: OrderID
    part_id: PartID
    qty: int
    price: Optional[float] = None
