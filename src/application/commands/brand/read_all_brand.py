from dataclasses import dataclass
from typing import List

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.brand_reader import BrandReader
from src.entities.brands.models import Brand
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_brand").bind(service="brand")


@dataclass
class ReadBrandResponse:
    uuid: str
    name: str

    @classmethod
    def from_entity(cls, entity: Brand) -> "ReadBrandResponse":
        return cls(uuid=str(entity.uuid), name=entity.name)


class ReadAllBrandCommandHandler(BaseCommandHandler):
    def __init__(self, brand_reader: BrandReader) -> None:
        self._brand_reader = brand_reader

    async def run(self, current_employee: Employee) -> List[ReadBrandResponse]:
        brands = await self._brand_reader.read_all_active()
        return [ReadBrandResponse.from_entity(b) for b in brands]
