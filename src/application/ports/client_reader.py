from typing import List, Optional, Protocol, Tuple
from src.entities.clients.models import Client, ClientID, ClientUUID


class ClientReader(Protocol):
    async def read_by_id(self, client_id: ClientID) -> Optional[Client]:
        ...

    async def read_by_uuid(self, client_uuid: ClientUUID) -> Optional[Client]:
        ...

    async def read_by_phone(self, phone: str) -> Optional[Client]:
        ...

    async def read_all_active(self, limit: int = 200, offset: int = 0) -> Tuple[List[Client], int]:
        ...
