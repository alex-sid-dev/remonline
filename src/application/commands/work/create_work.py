from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists, resolve_employee_id
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.application.ports.work_reader import WorkReader
from src.entities.orders.models import OrderUUID
from src.entities.works.services import WorkService

logger = structlog.get_logger("create_work").bind(service="work")


@dataclass(frozen=True, slots=True)
class CreateWorkCommandResponse:
    uuid: UUID


@dataclass(frozen=True, slots=True)
class CreateWorkCommand:
    order_uuid: UUID
    title: str
    employee_uuid: UUID | None = None
    description: str | None = None
    price: float | None = None
    qty: int = 1


class CreateWorkCommandHandler:
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
        order = await ensure_exists(
            self._order_reader.read_by_uuid, OrderUUID(data.order_uuid),
            f"Order with uuid {data.order_uuid}",
        )

        employee_id = await resolve_employee_id(self._employee_reader, data.employee_uuid)

        work = self._work_service.create_work(
            order_id=order.id,
            title=data.title,
            employee_id=employee_id,
            description=data.description,
            price=data.price,
            qty=data.qty,
        )
        self._entity_saver.add_one(work)
        await self._transaction.commit()
        logger.info("Work created successfully", work_uuid=str(work.uuid))
        return CreateWorkCommandResponse(
            uuid=work.uuid,
        )
