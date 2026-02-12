from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports.work_reader import WorkReader
from src.entities.works.models import Work, WorkID, WorkUUID
from src.entities.orders.models import OrderID

class WorkReaderAdapter(WorkReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, work_id: WorkID) -> Optional[Work]:
        stmt = select(Work).where(Work.id == work_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, work_uuid: WorkUUID) -> Optional[Work]:
        stmt = select(Work).where(Work.uuid == work_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all_active(self) -> List[Work]:
        stmt = select(Work).where(Work.is_active == True)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def read_by_order_id(self, order_id: OrderID) -> List[Work]:
        stmt = select(Work).where(Work.order_id == order_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
