from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports.part_reader import PartReader
from src.entities.parts.models import Part, PartID, PartUUID


class PartReaderAdapter(PartReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, part_id: PartID) -> Optional[Part]:
        stmt = select(Part).where(Part.id == part_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, part_uuid: PartUUID) -> Optional[Part]:
        stmt = select(Part).where(Part.uuid == part_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all_active(self, limit: int = 200, offset: int = 0) -> Tuple[List[Part], int]:
        count_stmt = select(func.count()).select_from(Part).where(Part.is_active.is_(True))
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Part)
            .where(Part.is_active.is_(True))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total
