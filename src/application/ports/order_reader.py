from typing import List, Optional, Protocol, Tuple
from src.entities.orders.models import Order, OrderID, OrderUUID
from src.entities.clients.models import ClientID


class OrderReader(Protocol):
    async def read_by_id(self, order_id: OrderID) -> Optional[Order]:
        ...

    async def read_by_uuid(self, order_uuid: OrderUUID) -> Optional[Order]:
        ...

    async def read_all_active(self, limit: int = 200, offset: int = 0) -> Tuple[List[Order], int]:
        ...

    async def read_by_client_id(self, client_id: ClientID) -> List[Order]:
        ...
