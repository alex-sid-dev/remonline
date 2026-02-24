from typing import Protocol

from src.entities.order_comments.models import OrderComment, OrderCommentUUID
from src.entities.orders.models import OrderID


class OrderCommentReader(Protocol):
    async def read_by_uuid(self, uuid: OrderCommentUUID) -> OrderComment | None: ...

    async def read_for_order(self, order_id: OrderID) -> list[OrderComment]: ...
