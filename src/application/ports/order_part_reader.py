from typing import Protocol, List, Optional
from src.entities.order_parts.models import OrderPart, OrderPartID, OrderPartUUID
from src.entities.orders.models import OrderID


class OrderPartReader(Protocol):
    async def read_by_id(self, order_part_id: OrderPartID) -> Optional[OrderPart]:
        ...

    async def read_by_uuid(self, order_part_uuid: OrderPartUUID) -> Optional[OrderPart]:
        ...

    async def read_all(self) -> List[OrderPart]:
        ...

    async def read_by_order_id(self, order_id: OrderID) -> List[OrderPart]:
        ...
