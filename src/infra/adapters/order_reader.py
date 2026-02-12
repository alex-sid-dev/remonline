from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports.order_reader import OrderReader
from src.entities.orders.models import Order, OrderID, OrderUUID
from src.entities.clients.models import ClientID

class OrderReaderAdapter(OrderReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, order_id: OrderID) -> Optional[Order]:
        stmt = select(Order).where(Order.id == order_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, order_uuid: OrderUUID) -> Optional[Order]:
        stmt = select(Order).where(Order.uuid == order_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all_active(self) -> List[Order]:
        stmt = select(Order).where(Order.is_active == True)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def read_by_client_id(self, client_id: ClientID) -> List[Order]:
        stmt = select(Order).where(Order.client_id == client_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
