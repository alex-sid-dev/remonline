from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports.order_part_reader import OrderPartReader
from src.entities.order_parts.models import OrderPart, OrderPartID, OrderPartUUID
from src.entities.orders.models import OrderID


class OrderPartReaderAdapter(OrderPartReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, order_part_id: OrderPartID) -> Optional[OrderPart]:
        stmt = select(OrderPart).where(OrderPart.id == order_part_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, order_part_uuid: OrderPartUUID) -> Optional[OrderPart]:
        stmt = select(OrderPart).where(OrderPart.uuid == order_part_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all(self) -> List[OrderPart]:
        stmt = select(OrderPart)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def read_by_order_id(self, order_id: OrderID) -> List[OrderPart]:
        stmt = (
            select(OrderPart)
            .where(OrderPart.order_id == order_id)
            .options(selectinload(OrderPart.part_info))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().unique().all())
