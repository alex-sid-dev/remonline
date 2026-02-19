from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.order_comment_reader import OrderCommentReader
from src.entities.order_comments.models import OrderComment, OrderCommentUUID
from src.entities.orders.models import OrderID


class OrderCommentReaderAdapter(OrderCommentReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_uuid(self, uuid: OrderCommentUUID) -> Optional[OrderComment]:
        stmt = select(OrderComment).where(OrderComment.uuid == uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_for_order(self, order_id: OrderID) -> List[OrderComment]:
        stmt = select(OrderComment).where(OrderComment.order_id == order_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
