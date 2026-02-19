from typing import List, Optional, Protocol, Tuple
from src.entities.parts.models import Part, PartID, PartUUID


class PartReader(Protocol):
    async def read_by_id(self, part_id: PartID) -> Optional[Part]:
        ...

    async def read_by_uuid(self, part_uuid: PartUUID) -> Optional[Part]:
        ...

    async def read_all_active(self, limit: int = 200, offset: int = 0) -> Tuple[List[Part], int]:
        ...
