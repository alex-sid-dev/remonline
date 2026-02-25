from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.application.ports.order_part_reader import OrderPartReader
from src.entities.order_parts.models import OrderPart, OrderPartID, OrderPartUUID
from src.entities.orders.models import OrderID
from src.entities.parts.models import PartID


class OrderPartReaderAdapter(OrderPartReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, order_part_id: OrderPartID) -> OrderPart | None:
        stmt = select(OrderPart).where(OrderPart.id == order_part_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, order_part_uuid: OrderPartUUID) -> OrderPart | None:
        stmt = select(OrderPart).where(OrderPart.uuid == order_part_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all(self) -> list[OrderPart]:
        stmt = select(OrderPart)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def read_by_order_id(self, order_id: OrderID) -> list[OrderPart]:
        stmt = (
            select(OrderPart)
            .where(OrderPart.order_id == order_id)
            .options(selectinload(OrderPart.part_info))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().unique().all())

    async def read_by_order_and_part(
        self, order_id: OrderID, part_id: PartID
    ) -> OrderPart | None:
        stmt = select(OrderPart).where(
            OrderPart.order_id == order_id, OrderPart.part_id == part_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
