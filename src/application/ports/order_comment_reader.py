from typing import List, Optional, Protocol

from src.entities.order_comments.models import OrderComment, OrderCommentUUID
from src.entities.orders.models import OrderID


class OrderCommentReader(Protocol):
    async def read_by_uuid(self, uuid: OrderCommentUUID) -> Optional[OrderComment]: ...

    async def read_for_order(self, order_id: OrderID) -> List[OrderComment]: ...
