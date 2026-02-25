from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import structlog
from pydantic import BaseModel

from src.application.ports.order_reader import OrderReader
from src.entities.employees.models import Employee
from src.entities.orders.models import Order

logger = structlog.get_logger("read_all_order").bind(service="order")


@dataclass(frozen=True, slots=True)
class ReadAllOrderCommand:
    limit: int = 200
    offset: int = 0


class ReadOrderResponse(BaseModel):
    id: int
    uuid: UUID
    client_name: str
    client_phone: str
    device_label: str
    creator_name: str
    assigned_employee_name: str
    status: str
    problem_description: str | None = None
    price: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

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
            uuid=entity.uuid,
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


class PaginatedOrderResponse(BaseModel):
    items: list[ReadOrderResponse]
    total: int
    limit: int
    offset: int


class ReadAllOrderCommandHandler:
    def __init__(self, order_reader: OrderReader) -> None:
        self._order_reader = order_reader

    async def run(
        self, data: ReadAllOrderCommand, current_employee: Employee
    ) -> PaginatedOrderResponse:
        orders, total = await self._order_reader.read_all_active(data.limit, data.offset)
        return PaginatedOrderResponse(
            items=[ReadOrderResponse.from_entity(o) for o in orders],
            total=total,
            limit=data.limit,
            offset=data.offset,
        )
