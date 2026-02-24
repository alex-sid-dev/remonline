from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.organization_reader import OrganizationReader
from src.entities.organizations.models import Organization


class OrganizationReaderAdapter(OrganizationReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_single(self) -> Organization | None:
        stmt = select(Organization).where(Organization.singleton_key == 1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
