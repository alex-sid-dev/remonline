from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity

OrganizationID = NewType("OrganizationID", int)
OrganizationUUID = NewType("OrganizationUUID", UUID)


@dataclass
class Organization(BaseEntity[OrganizationID, OrganizationUUID]):
    """Единственная запись в БД (singleton_key = 1 unique)."""

    singleton_key: int = 1
    name: str = ""
    inn: str = ""
    address: str | None = None
    kpp: str | None = None
    bank_account: str | None = None  # Р/с
    corr_account: str | None = None  # К/с
    bik: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
