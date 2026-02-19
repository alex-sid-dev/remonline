from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports.client_reader import ClientReader
from src.entities.clients.models import Client, ClientID, ClientUUID


class ClientReaderAdapter(ClientReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, client_id: ClientID) -> Optional[Client]:
        stmt = select(Client).where(Client.id == client_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, client_uuid: ClientUUID) -> Optional[Client]:
        stmt = select(Client).where(Client.uuid == client_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_phone(self, phone: str) -> Optional[Client]:
        stmt = select(Client).where(Client.phone == phone)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all_active(self, limit: int = 200, offset: int = 0) -> Tuple[List[Client], int]:
        count_stmt = select(func.count()).select_from(Client).where(Client.is_active.is_(True))
        total = (await self._session.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Client)
            .where(Client.is_active.is_(True))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total
