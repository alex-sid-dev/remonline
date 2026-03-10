from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.order_reader import OrderReader
from src.entities.clients.models import ClientID
from src.entities.orders.models import Order, OrderID, OrderUUID


class OrderReaderAdapter(OrderReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, order_id: OrderID) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, order_uuid: OrderUUID) -> Order | None:
        stmt = select(Order).where(Order.uuid == order_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all_active(
        self,
        organization_id: int,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[list[Order], int]:
        count_stmt = (
            select(func.count())
            .select_from(Order)
            .where(Order.is_active.is_(True), Order.organization_id == organization_id)
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Order)
            .where(Order.is_active.is_(True), Order.organization_id == organization_id)
            .order_by(Order.id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total

    async def read_by_client_id(self, client_id: ClientID) -> list[Order]:
        stmt = select(Order).where(Order.client_id == client_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
