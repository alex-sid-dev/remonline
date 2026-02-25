from dataclasses import dataclass
from uuid import UUID

import structlog
from src.application.commands._helpers import ensure_exists
from src.application.ports.brand_reader import BrandReader
from src.application.ports.transaction import Transaction
from src.entities.brands.models import BrandUUID
from src.entities.brands.services import BrandService
from src.entities.employees.models import Employee

logger = structlog.get_logger("update_brand").bind(service="brand")


@dataclass(frozen=True, slots=True)
class UpdateBrandCommand:
    uuid: UUID
    name: str | None = None
    is_active: bool | None = None


class UpdateBrandCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        brand_reader: BrandReader,
        brand_service: BrandService,
    ) -> None:
        self._transaction = transaction
        self._brand_reader = brand_reader
        self._brand_service = brand_service

    async def run(self, data: UpdateBrandCommand, current_employee: Employee) -> None:
        brand = await ensure_exists(
            self._brand_reader.read_by_uuid,
            BrandUUID(data.uuid),
            f"Brand {data.uuid}",
        )
        self._brand_service.update_brand(brand, name=data.name, is_active=data.is_active)
        await self._transaction.commit()
        logger.info("Brand updated", brand_uuid=str(data.uuid))
