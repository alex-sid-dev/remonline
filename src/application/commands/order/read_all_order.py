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
    limit: int = 200
    offset: int = 0


@dataclass
class ReadOrderResponse:
    id: int
    uuid: str
    client_name: str
    client_phone: str
    device_label: str
    creator_name: str
    assigned_employee_name: str
    status: str
    problem_description: Optional[str]
    price: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_entity(cls, entity: Order) -> "ReadOrderResponse":
        client = getattr(entity, "client", None)
        device = getattr(entity, "device", None)
        creator = getattr(entity, "creator", None)
        assigned = getattr(entity, "assigned_employee", None)

        device_label = "—"
        if device:
            brand_name = device.brand.name if getattr(device, "brand", None) else "—"
            device_label = f"{brand_name} {device.model}".strip()
            if device.serial_number:
                device_label += f" · SN: {device.serial_number}"

        return cls(
            id=entity.id,
            uuid=str(entity.uuid),
            client_name=client.full_name if client else "—",
            client_phone=client.phone if client else "—",
            device_label=device_label,
            creator_name=creator.full_name if creator else "—",
            assigned_employee_name=assigned.full_name if assigned else "—",
            status=entity.status,
            problem_description=entity.problem_description,
            price=entity.price,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


@dataclass
class PaginatedOrderResponse:
    items: List[ReadOrderResponse]
    total: int
    limit: int
    offset: int


class ReadAllOrderCommandHandler(BaseCommandHandler):
    def __init__(self, order_reader: OrderReader) -> None:
        self._order_reader = order_reader

    async def run(self, data: ReadAllOrderCommand, current_employee: Employee) -> PaginatedOrderResponse:
        orders, total = await self._order_reader.read_all_active(data.limit, data.offset)
        return PaginatedOrderResponse(
            items=[ReadOrderResponse.from_entity(o) for o in orders],
            total=total,
            limit=data.limit,
            offset=data.offset,
        )
