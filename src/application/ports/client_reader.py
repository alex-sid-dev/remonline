from abc import ABC, abstractmethod
from typing import List
from src.entities.clients.models import Client, ClientID, ClientUUID

class ClientReader(ABC):
    """Read-only repository for Client entities."""

    @abstractmethod
    async def read_by_oid(self, client_oid: ClientID) -> Client | None: ...

    @abstractmethod
    async def read_by_uuid(self, client_uuid: ClientUUID) -> Client | None: ...

    @abstractmethod
    async def read_by_phone(self, phone: str) -> Client | None: ...

    @abstractmethod
    async def read_all_active(self) -> List[Client]: ...
