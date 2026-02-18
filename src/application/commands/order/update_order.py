from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.application.ports.transaction import Transaction
from src.entities.orders.models import OrderUUID
from src.entities.orders.services import OrderService
from src.entities.employees.models import Employee, EmployeeID
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("update_order").bind(service="order")

@dataclass
class UpdateOrderCommand:
    uuid: UUID
    assigned_employee_id: Optional[int] = None
    status: Optional[str] = None
    problem_description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None

class UpdateOrderCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            order_reader: OrderReader,
            order_service: OrderService,
    ) -> None:
        self._transaction = transaction
        self._order_reader = order_reader
        self._order_service = order_service

    async def run(self, data: UpdateOrderCommand, current_employee: Employee) -> None:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.uuid))
        if not order:
            raise EntityNotFoundError(f"Order with uuid {data.uuid} not found")

        self._order_service.update_order(
            order=order,
            assigned_employee_id=EmployeeID(data.assigned_employee_id) if data.assigned_employee_id is not None else None,
            status=data.status,
            problem_description=data.problem_description,
            comment=data.comment,
            price=data.price,
            is_active=data.is_active
        )
        await self._transaction.commit()
        logger.info("Order updated successfully", order_uuid=str(data.uuid))
