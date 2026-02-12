from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports.payment_reader import PaymentReader
from src.entities.payments.models import Payment, PaymentID, PaymentUUID
from src.entities.orders.models import OrderID

class PaymentReaderAdapter(PaymentReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, payment_id: PaymentID) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, payment_uuid: PaymentUUID) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.uuid == payment_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all(self) -> List[Payment]:
        stmt = select(Payment)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def read_by_order_id(self, order_id: OrderID) -> List[Payment]:
        stmt = select(Payment).where(Payment.order_id == order_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
