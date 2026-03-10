from typing import Protocol

from src.entities.parts.models import Part, PartID, PartUUID


class PartReader(Protocol):
    async def read_by_id(self, part_id: PartID) -> Part | None: ...

    async def read_by_uuid(self, part_uuid: PartUUID) -> Part | None: ...

    async def read_all_active(
        self,
        organization_id: int,
        limit: int = 200,
        offset: int = 0,
    ) -> tuple[list[Part], int]: ...
