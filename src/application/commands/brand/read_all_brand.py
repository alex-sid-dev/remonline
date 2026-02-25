from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict

from src.application.ports.brand_reader import BrandReader
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_brand").bind(service="brand")


class ReadBrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str


class ReadAllBrandCommandHandler:
    def __init__(self, brand_reader: BrandReader) -> None:
        self._brand_reader = brand_reader

    async def run(self, current_employee: Employee) -> list[ReadBrandResponse]:
        brands = await self._brand_reader.read_all_active()
        return [ReadBrandResponse.model_validate(b) for b in brands]
