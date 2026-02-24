from typing import Protocol

from src.entities.organizations.models import Organization


class OrganizationReader(Protocol):
    """Чтение единственной организации (singleton)."""

    async def get_single(self) -> Organization | None: ...
