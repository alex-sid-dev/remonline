from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import structlog
from src.application.commands._helpers import ensure_exists
from src.application.commands.brand.read_all_brand import ReadBrandResponse
from src.application.ports.brand_reader import BrandReader
from src.entities.brands.models import BrandUUID
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_brand").bind(service="brand")


@dataclass(frozen=True, slots=True)
class ReadBrandCommand:
    uuid: UUID


class ReadBrandCommandHandler:
    def __init__(self, brand_reader: BrandReader) -> None:
        self._brand_reader = brand_reader

    async def run(self, data: ReadBrandCommand, current_employee: Employee) -> ReadBrandResponse:
        brand = await ensure_exists(
            self._brand_reader.read_by_uuid,
            BrandUUID(data.uuid),
            f"Brand {data.uuid}",
        )
        return ReadBrandResponse.model_validate(brand)
