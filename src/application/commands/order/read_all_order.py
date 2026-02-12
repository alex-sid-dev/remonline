from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.entities.orders.models import Order
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_order").bind(service="order")

@dataclass
class ReadAllOrderCommand:
    pass

@dataclass
class ReadOrderResponse:
    id: int
    uuid: str
    client_id: int
    device_id: int
    creator_id: Optional[int]
    assigned_employee_id: Optional[int]
    status: str
    problem_description: Optional[str]
    comment: Optional[str]
    price: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_entity(cls, entity: Order) -> "ReadOrderResponse":
        return cls(
            id=entity.id,
            uuid=str(entity.uuid),
            client_id=entity.client_id,
            device_id=entity.device_id,
            creator_id=entity.creator_id,
            assigned_employee_id=entity.assigned_employee_id,
            status=entity.status,
            problem_description=entity.problem_description,
            comment=entity.comment,
            price=entity.price,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

class ReadAllOrderCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            order_reader: OrderReader,
    ) -> None:
        self._order_reader = order_reader

    async def run(self, data: ReadAllOrderCommand, current_employee: Employee) -> List[ReadOrderResponse]:
        orders = await self._order_reader.read_all_active()
        return [ReadOrderResponse.from_entity(o) for o in orders]
