from typing import Protocol

from src.entities.clients.models import Client, ClientID, ClientUUID


class ClientReader(Protocol):
    async def read_by_id(self, client_id: ClientID) -> Client | None: ...

    async def read_by_uuid(self, client_uuid: ClientUUID) -> Client | None: ...

    async def read_by_phone(self, phone: str) -> Client | None: ...

    async def read_all_active(
        self,
        organization_id: int,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[list[Client], int]: ...
