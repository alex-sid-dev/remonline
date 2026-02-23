from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.brand_reader import BrandReader
from src.entities.brands.models import Brand, BrandUUID
from src.entities.employees.models import Employee
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("read_brand").bind(service="brand")


@dataclass
class ReadBrandCommand:
    uuid: UUID


@dataclass
class ReadBrandResponse:
    uuid: str
    name: str

    @classmethod
    def from_entity(cls, entity: Brand) -> "ReadBrandResponse":
        return cls(uuid=str(entity.uuid), name=entity.name)


class ReadBrandCommandHandler(BaseCommandHandler):
    def __init__(self, brand_reader: BrandReader) -> None:
        self._brand_reader = brand_reader

    async def run(self, data: ReadBrandCommand, current_employee: Employee) -> ReadBrandResponse:
        brand = await self._brand_reader.read_by_uuid(BrandUUID(data.uuid))
        if not brand:
            raise EntityNotFoundError(message=f"Brand {data.uuid} not found")
        return ReadBrandResponse.from_entity(brand)
