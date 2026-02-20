from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Optional
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
    address: Optional[str] = None
    kpp: Optional[str] = None
    bank_account: Optional[str] = None  # Р/с
    corr_account: Optional[str] = None  # К/с
    bik: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
