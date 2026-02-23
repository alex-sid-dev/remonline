from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.brand_reader import BrandReader
from src.entities.brands.models import Brand, BrandID, BrandUUID


class BrandReaderAdapter(BrandReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, brand_id: BrandID) -> Optional[Brand]:
        stmt = select(Brand).where(Brand.id == brand_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, brand_uuid: BrandUUID) -> Optional[Brand]:
        stmt = select(Brand).where(Brand.uuid == brand_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all_active(self) -> List[Brand]:
        stmt = select(Brand).where(Brand.is_active.is_(True)).order_by(Brand.name.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
