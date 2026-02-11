import structlog
from typing import Final, Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.clients.models import Client, ClientID, ClientUUID
from src.infra.models.clients import clients_table
from src.application.ports.client_reader import ClientReader


class ClientReaderAlchemy(ClientReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final = session
        self._logger = structlog.get_logger("db").bind(service="db", entity="client")

    async def read_by_oid(self, client_oid: ClientID) -> Client | None:
        self._logger.info("Reading client by OID", client_oid=str(client_oid))
        stmt = select(Client).where(clients_table.c.client_id == client_oid)
        result = await self._session.execute(stmt)
        client = result.scalar_one_or_none()
        if client is None:
            self._logger.warning("Client not found by OID", client_oid=str(client_oid))
        else:
            self._logger.info("Client found", client_id=client.client_id)
        return client

    async def read_by_uuid(self, client_uuid: ClientUUID) -> Client | None:
        self._logger.info("Reading client by UUID", client_uuid=str(client_uuid))
        stmt = select(Client).where(clients_table.c.client_uuid == client_uuid)
        result = await self._session.execute(stmt)
        client = result.scalar_one_or_none()
        if client is None:
            self._logger.warning("Client not found by UUID", client_uuid=str(client_uuid))
        else:
            self._logger.info("Client found", client_id=client.client_id)
        return client

    async def read_by_phone(self, phone: str) -> Client | None:
        self._logger.info("Reading client by phone", phone=phone)
        stmt = select(Client).where(clients_table.c.phone == phone)
        result = await self._session.execute(stmt)
        client = result.scalar_one_or_none()
        if client is None:
            self._logger.warning("Client not found by phone", phone=phone)
        else:
            self._logger.info("Client found", client_id=client.client_id)
        return client

    async def read_all_active(self) -> Sequence[Any]:
        self._logger.info("Reading all active clients")
        stmt = select(Client).where(clients_table.c.is_active == True)
        result = await self._session.execute(stmt)
        clients = result.scalars().all()
        self._logger.info("Number of active clients found", count=len(clients))
        return clients
