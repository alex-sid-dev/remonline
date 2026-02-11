from dataclasses import dataclass
from typing import Optional, NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity

ClientID = NewType("ClientID", int)
ClientUUID = NewType("ClientUUID", UUID)


@dataclass
class Client(BaseEntity[ClientID, ClientUUID]):
    full_name: str
    phone: str
    email: Optional[str] = None
    telegram_nick: Optional[str] = None
    comment: Optional[str] = None
    is_active: bool = True
