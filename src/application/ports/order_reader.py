from typing import Protocol

from src.entities.clients.models import ClientID
from src.entities.orders.models import Order, OrderID, OrderUUID


class OrderReader(Protocol):
    async def read_by_id(self, order_id: OrderID) -> Order | None: ...

    async def read_by_uuid(self, order_uuid: OrderUUID) -> Order | None: ...

    async def read_all_active(
        self, limit: int = 200, offset: int = 0
    ) -> tuple[list[Order], int]: ...

    async def read_by_client_id(self, client_id: ClientID) -> list[Order]: ...
