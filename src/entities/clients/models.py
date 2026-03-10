from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.organizations.models import OrganizationID

ClientID = NewType("ClientID", int)
ClientUUID = NewType("ClientUUID", UUID)


@dataclass
class Client(BaseEntity[ClientID, ClientUUID]):
    full_name: str
    phone: str
    organization_id: OrganizationID
    email: str | None = None
    telegram_nick: str | None = None
    comment: str | None = None
    address: str | None = None
    is_active: bool = True
