from typing import Protocol

from src.entities.orders.models import OrderID
from src.entities.payments.models import Payment, PaymentID, PaymentUUID


class PaymentReader(Protocol):
    async def read_by_id(self, payment_id: PaymentID) -> Payment | None: ...

    async def read_by_uuid(self, payment_uuid: PaymentUUID) -> Payment | None: ...

    async def read_all(self) -> list[Payment]: ...

    async def read_by_order_id(self, order_id: OrderID) -> list[Payment]: ...
