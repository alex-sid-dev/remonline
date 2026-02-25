from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists, resolve_employee_id
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction
from src.application.ports.work_reader import WorkReader
from src.entities.employees.models import Employee, EmployeeID
from src.entities.works.models import WorkUUID
from src.entities.works.services import WorkService

logger = structlog.get_logger("update_work").bind(service="work")


@dataclass(frozen=True, slots=True)
class UpdateWorkCommand:
    uuid: UUID
    title: str | None = None
    employee_uuid: UUID | None = None
    description: str | None = None
    price: float | None = None
    qty: int | None = None
    is_active: bool | None = None


class UpdateWorkCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        work_reader: WorkReader,
        work_service: WorkService,
        employee_reader: EmployeeReader,
    ) -> None:
        self._transaction = transaction
        self._work_reader = work_reader
        self._work_service = work_service
        self._employee_reader = employee_reader

    async def run(self, data: UpdateWorkCommand, current_employee: Employee) -> None:
        work = await ensure_exists(
            self._work_reader.read_by_uuid,
            WorkUUID(data.uuid),
            f"Work with uuid {data.uuid}",
        )

        employee_id = await resolve_employee_id(self._employee_reader, data.employee_uuid)

        self._work_service.update_work(
            work=work,
            title=data.title,
            employee_id=EmployeeID(employee_id) if employee_id is not None else None,
            description=data.description,
            price=data.price,
            qty=data.qty,
            is_active=data.is_active,
        )
        await self._transaction.commit()
        logger.info("Work updated successfully", work_uuid=str(data.uuid))
