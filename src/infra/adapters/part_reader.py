from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.part_reader import PartReader
from src.entities.parts.models import Part, PartID, PartUUID


class PartReaderAdapter(PartReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, part_id: PartID) -> Part | None:
        stmt = select(Part).where(Part.id == part_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, part_uuid: PartUUID) -> Part | None:
        stmt = select(Part).where(Part.uuid == part_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all_active(
        self,
        organization_id: int,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[list[Part], int]:
        count_stmt = (
            select(func.count())
            .select_from(Part)
            .where(Part.is_active.is_(True), Part.organization_id == organization_id)
        )
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Part)
            .where(Part.is_active.is_(True), Part.organization_id == organization_id)
            .order_by(Part.id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total
