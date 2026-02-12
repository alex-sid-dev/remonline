from typing import List, Optional, Protocol
from src.entities.payments.models import Payment, PaymentID, PaymentUUID
from src.entities.orders.models import OrderID

class PaymentReader(Protocol):
    async def read_by_id(self, payment_id: PaymentID) -> Optional[Payment]:
        ...

    async def read_by_uuid(self, payment_uuid: PaymentUUID) -> Optional[Payment]:
        ...

    async def read_all(self) -> List[Payment]:
        ...

    async def read_by_order_id(self, order_id: OrderID) -> List[Payment]:
        ...
