from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity

ClientID = NewType("ClientID", int)
ClientUUID = NewType("ClientUUID", UUID)


@dataclass
class Client(BaseEntity[ClientID, ClientUUID]):
    full_name: str
    phone: str
    email: str | None = None
    telegram_nick: str | None = None
    comment: str | None = None
    address: str | None = None
    is_active: bool = True
