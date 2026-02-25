from typing import Protocol

from src.entities.order_parts.models import OrderPart, OrderPartID, OrderPartUUID
from src.entities.orders.models import OrderID
from src.entities.parts.models import PartID


class OrderPartReader(Protocol):
    async def read_by_id(self, order_part_id: OrderPartID) -> OrderPart | None: ...

    async def read_by_uuid(self, order_part_uuid: OrderPartUUID) -> OrderPart | None: ...

    async def read_all(self) -> list[OrderPart]: ...

    async def read_by_order_id(self, order_id: OrderID) -> list[OrderPart]: ...

    async def read_by_order_and_part(
        self, order_id: OrderID, part_id: PartID
    ) -> OrderPart | None: ...
