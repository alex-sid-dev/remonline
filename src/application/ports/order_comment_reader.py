from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.entities.order_comments.models import OrderComment, OrderCommentID, OrderCommentUUID
from src.entities.orders.models import OrderID, OrderUUID


class OrderCommentReader(ABC):
    @abstractmethod
    async def read_by_uuid(self, uuid: OrderCommentUUID) -> Optional[OrderComment]:
        raise NotImplementedError

    @abstractmethod
    async def read_for_order(self, order_id: OrderID) -> List[OrderComment]:
        raise NotImplementedError

