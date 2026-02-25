from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import (
    ensure_exists,
    resolve_employee_id,
    resolve_order_creator_id,
)
from src.application.ports.client_reader import ClientReader
from src.application.ports.device_reader import DeviceReader
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.clients.models import ClientUUID
from src.entities.devices.models import DeviceUUID
from src.entities.orders.services import OrderService

logger = structlog.get_logger("create_order").bind(service="order")


@dataclass(frozen=True, slots=True)
class CreateOrderCommandResponse:
    uuid: UUID


@dataclass(frozen=True, slots=True)
class CreateOrderCommand:
    client_uuid: UUID
    device_uuid: UUID
    problem_description: str | None = None
    assigned_employee_uuid: UUID | None = None
    manager_uuid: UUID | None = None
    status: str = "new"
    price: float | None = None


class CreateOrderCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        order_service: OrderService,
        order_reader: OrderReader,
        client_reader: ClientReader,
        device_reader: DeviceReader,
        employee_reader: EmployeeReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._order_reader = order_reader
        self._order_service = order_service
        self._client_reader = client_reader
        self._device_reader = device_reader
        self._employee_reader = employee_reader

    async def run(self, data: CreateOrderCommand, current_employee) -> CreateOrderCommandResponse:
        client = await ensure_exists(
            self._client_reader.read_by_uuid,
            ClientUUID(data.client_uuid),
            f"Client with uuid {data.client_uuid}",
        )
        device = await ensure_exists(
            self._device_reader.read_by_uuid,
            DeviceUUID(data.device_uuid),
            f"Device with uuid {data.device_uuid}",
        )

        assigned_employee_id = await resolve_employee_id(
            self._employee_reader, data.assigned_employee_uuid
        )
        creator_id = await resolve_order_creator_id(
            self._employee_reader, data.manager_uuid, current_employee
        )

        order = self._order_service.create_order(
            client_id=client.id,
            device_id=device.id,
            creator_id=creator_id,
            problem_description=data.problem_description,
            assigned_employee_id=assigned_employee_id,
            status=data.status,
            price=data.price,
        )
        self._entity_saver.add_one(order)
        await self._transaction.commit()
        logger.info("Order created successfully", order_uuid=str(order.uuid))
        return CreateOrderCommandResponse(
            uuid=order.uuid,
        )
