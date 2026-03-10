from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity
from src.entities.organizations.models import OrganizationID

BrandID = NewType("BrandID", int)
BrandUUID = NewType("BrandUUID", UUID)


@dataclass
class Brand(BaseEntity[BrandID, BrandUUID]):
    """Бренд устройства (Samsung, Apple и т.д.)."""

    name: str
    organization_id: OrganizationID
    is_active: bool = True
