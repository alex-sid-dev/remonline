from typing import Protocol

from src.entities.brands.models import Brand, BrandID, BrandUUID


class BrandReader(Protocol):
    async def read_by_id(self, brand_id: BrandID) -> Brand | None: ...

    async def read_by_uuid(self, brand_uuid: BrandUUID) -> Brand | None: ...

    async def read_all_active(self) -> list[Brand]: ...
