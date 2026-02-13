from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.work_reader import WorkReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.works.services import WorkService
from src.entities.employees.models import Employee, EmployeeUUID
from src.entities.orders.models import OrderUUID
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("create_work").bind(service="work")


@dataclass
class CreateWorkCommandResponse:
    uuid: UUID


@dataclass
class CreateWorkCommand:
    order_uuid: UUID
    title: str
    employee_uuid: Optional[UUID] = None
    description: Optional[str] = None
    price: Optional[float] = None


class CreateWorkCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            entity_saver: EntitySaver,
            work_service: WorkService,
            work_reader: WorkReader,
            order_reader: OrderReader,
            employee_reader: EmployeeReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._work_reader = work_reader
        self._work_service = work_service
        self._order_reader = order_reader
        self._employee_reader = employee_reader

    async def run(self, data: CreateWorkCommand) -> CreateWorkCommandResponse:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.order_uuid))
        if not order:
            raise EntityNotFoundError(message=f"Order with uuid {data.order_uuid} not found")

        employee_id = None
        if data.employee_uuid:
            employee = await self._employee_reader.read_by_uuid(EmployeeUUID(data.employee_uuid))
            if not employee:
                raise EntityNotFoundError(message=f"Employee with uuid {data.employee_uuid} not found")
            employee_id = employee.id

        work = self._work_service.create_work(
            order_id=order.id,
            title=data.title,
            employee_id=employee_id,
            description=data.description,
            price=data.price
        )
        self._entity_saver.add_one(work)
        await self._transaction.commit()
        logger.info("Work created successfully", work_uuid=str(work.uuid))
        return CreateWorkCommandResponse(
            uuid=work.uuid,
        )
