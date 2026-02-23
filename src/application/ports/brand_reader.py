from typing import List, Optional, Protocol

from src.entities.brands.models import Brand, BrandID, BrandUUID


class BrandReader(Protocol):
    async def read_by_id(self, brand_id: BrandID) -> Optional[Brand]:
        ...

    async def read_by_uuid(self, brand_uuid: BrandUUID) -> Optional[Brand]:
        ...

    async def read_all_active(self) -> List[Brand]:
        ...
