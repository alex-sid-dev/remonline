from typing import Optional
from uuid import uuid4

from src.entities.brands.models import Brand, BrandID, BrandUUID


class BrandService:
    """Создание и обновление брендов."""

    def create_brand(self, name: str) -> Brand:
        return Brand(
            id=None,  # type: ignore
            uuid=BrandUUID(uuid4()),
            name=name.strip(),
            is_active=True,
        )

    def update_brand(
        self,
        brand: Brand,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Brand:
        if name is not None:
            brand.name = name.strip()
        if is_active is not None:
            brand.is_active = is_active
        return brand
