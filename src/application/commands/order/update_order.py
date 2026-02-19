from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.work_reader import WorkReader
from src.application.ports.transaction import Transaction
from src.entities.orders.models import OrderUUID
from src.entities.orders.services import OrderService
from src.entities.employees.models import Employee, EmployeeID, EmployeeUUID
from src.entities.employees.enum import EmployeePosition
from src.entities.orders.enum import OrderStatus
from src.application.errors._base import EntityNotFoundError, PermissionDeniedError

logger = structlog.get_logger("update_order").bind(service="order")


@dataclass
class UpdateOrderCommand:
    uuid: UUID
    assigned_employee_uuid: Optional[UUID] = None
    creator_uuid: Optional[UUID] = None
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
            employee_reader: EmployeeReader,
            work_reader: WorkReader,
    ) -> None:
        self._transaction = transaction
        self._order_reader = order_reader
        self._order_service = order_service
        self._employee_reader = employee_reader
        self._work_reader = work_reader

    async def run(self, data: UpdateOrderCommand, current_employee: Employee) -> None:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.uuid))
        if not order:
            raise EntityNotFoundError(message=f"Order with uuid {data.uuid} not found")

        if data.status == OrderStatus.CLOSED.value and current_employee.position != EmployeePosition.SUPERVISOR:
            raise PermissionDeniedError(message="Только супервайзер может закрывать заказы")

        assigned_employee_id = None
        if data.assigned_employee_uuid is not None:
            emp = await self._employee_reader.read_by_uuid(EmployeeUUID(data.assigned_employee_uuid))
            if not emp:
                raise EntityNotFoundError(message=f"Employee with uuid {data.assigned_employee_uuid} not found")
            assigned_employee_id = emp.id

        creator_id = None
        if data.creator_uuid is not None:
            emp = await self._employee_reader.read_by_uuid(EmployeeUUID(data.creator_uuid))
            if not emp:
                raise EntityNotFoundError(message=f"Employee with uuid {data.creator_uuid} not found")
            creator_id = emp.id

        self._order_service.update_order(
            order=order,
            creator_id=EmployeeID(creator_id) if creator_id is not None else None,
            assigned_employee_id=EmployeeID(assigned_employee_id) if assigned_employee_id is not None else None,
            status=data.status,
            problem_description=data.problem_description,
            price=data.price,
            is_active=data.is_active,
        )

        if assigned_employee_id is not None:
            works = await self._work_reader.read_by_order_id(order.id)
            updated_works = self._order_service.assign_engineer_to_unassigned_works(
                works, EmployeeID(assigned_employee_id)
            )
            for work in updated_works:
                logger.info(
                    "Auto-assigned engineer to work",
                    work_uuid=str(work.uuid),
                    employee_id=assigned_employee_id,
                )

        await self._transaction.commit()
        logger.info("Order updated successfully", order_uuid=str(data.uuid))
