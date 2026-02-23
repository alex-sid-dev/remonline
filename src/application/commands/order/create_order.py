from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.application.ports.client_reader import ClientReader
from src.application.ports.device_reader import DeviceReader
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.orders.services import OrderService
from src.entities.orders.models import Order
from src.entities.clients.models import ClientUUID
from src.entities.devices.models import DeviceUUID
from src.entities.employees.models import Employee, EmployeeUUID, EmployeePosition
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("create_order").bind(service="order")


@dataclass
class CreateOrderCommandResponse:
    uuid: UUID


@dataclass
class CreateOrderCommand:
    client_uuid: UUID
    device_uuid: UUID
    problem_description: Optional[str] = None
    assigned_employee_uuid: Optional[UUID] = None
    manager_uuid: Optional[UUID] = None
    status: str = "new"
    price: Optional[float] = None


class CreateOrderCommandHandler(BaseCommandHandler):
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
        client = await self._client_reader.read_by_uuid(ClientUUID(data.client_uuid))
        if not client:
            raise EntityNotFoundError(message=f"Client with uuid {data.client_uuid} not found")

        device = await self._device_reader.read_by_uuid(DeviceUUID(data.device_uuid))
        if not device:
            raise EntityNotFoundError(message=f"Device with uuid {data.device_uuid} not found")

        assigned_employee_id = None
        if data.assigned_employee_uuid:
            assigned_employee = await self._employee_reader.read_by_uuid(EmployeeUUID(data.assigned_employee_uuid))
            if not assigned_employee:
                raise EntityNotFoundError(message=f"Employee with uuid {data.assigned_employee_uuid} not found")
            assigned_employee_id = assigned_employee.id

        # Определяем менеджера (creator_id):
        # - если передан manager_uuid — используем его; назначить менеджером заказа нельзя только мастера;
        # - если заказ создаёт менеджер — он сам становится менеджером заказа;
        # - иначе (админ/супервизор/мастер) — creator_id = current_employee.id.
        creator_id = current_employee.id
        if data.manager_uuid:
            manager = await self._employee_reader.read_by_uuid(EmployeeUUID(data.manager_uuid))
            if not manager:
                raise EntityNotFoundError(message=f"Employee with uuid {data.manager_uuid} not found")
            if manager.position == EmployeePosition.MASTER:
                raise EntityNotFoundError(message="Назначить менеджером нельзя сотрудника с ролью мастер.")
            creator_id = manager.id
        elif getattr(current_employee, "position", None) == EmployeePosition.MANAGER:
            creator_id = current_employee.id

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
