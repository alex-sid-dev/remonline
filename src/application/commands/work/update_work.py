from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction
from src.application.ports.work_reader import WorkReader
from src.entities.employees.models import Employee, EmployeeID, EmployeeUUID
from src.entities.works.models import WorkUUID
from src.entities.works.services import WorkService

logger = structlog.get_logger("update_work").bind(service="work")


@dataclass
class UpdateWorkCommand:
    uuid: UUID
    title: str | None = None
    employee_uuid: UUID | None = None
    description: str | None = None
    price: float | None = None
    qty: int | None = None
    is_active: bool | None = None


class UpdateWorkCommandHandler(BaseCommandHandler):
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
        work = await self._work_reader.read_by_uuid(WorkUUID(data.uuid))
        if not work:
            raise EntityNotFoundError(f"Work with uuid {data.uuid} not found")

        employee_id = None
        if data.employee_uuid is not None:
            emp = await self._employee_reader.read_by_uuid(EmployeeUUID(data.employee_uuid))
            if not emp:
                raise EntityNotFoundError(f"Employee with uuid {data.employee_uuid} not found")
            employee_id = emp.id

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
