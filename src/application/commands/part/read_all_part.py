from dataclasses import dataclass
from typing import List, Optional
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.part_reader import PartReader
from src.entities.parts.models import Part
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_part").bind(service="part")

@dataclass
class ReadAllPartCommand:
    pass

@dataclass
class ReadPartResponse:
    id: int
    uuid: str
    name: str
    sku: Optional[str]
    price: Optional[float]
    stock_qty: Optional[int]

    @classmethod
    def from_entity(cls, entity: Part) -> "ReadPartResponse":
        return cls(
            id=entity.id,
            uuid=str(entity.uuid),
            name=entity.name,
            sku=entity.sku,
            price=entity.price,
            stock_qty=entity.stock_qty
        )

class ReadAllPartCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            part_reader: PartReader,
    ) -> None:
        self._part_reader = part_reader

    async def run(self, data: ReadAllPartCommand, current_employee: Employee) -> List[ReadPartResponse]:
        parts = await self._part_reader.read_all_active()
        return [ReadPartResponse.from_entity(p) for p in parts]
