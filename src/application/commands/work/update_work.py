from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.work_reader import WorkReader
from src.application.ports.transaction import Transaction
from src.entities.works.models import WorkUUID
from src.entities.works.services import WorkService
from src.entities.employees.models import Employee, EmployeeID
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("update_work").bind(service="work")

@dataclass
class UpdateWorkCommand:
    uuid: UUID
    title: Optional[str] = None
    employee_id: Optional[int] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None

class UpdateWorkCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            work_reader: WorkReader,
            work_service: WorkService,
    ) -> None:
        self._transaction = transaction
        self._work_reader = work_reader
        self._work_service = work_service

    async def run(self, data: UpdateWorkCommand, current_employee: Employee) -> None:
        work = await self._work_reader.read_by_uuid(WorkUUID(data.uuid))
        if not work:
            raise EntityNotFoundError(f"Work with uuid {data.uuid} not found")

        self._work_service.update_work(
            work=work,
            title=data.title,
            employee_id=EmployeeID(data.employee_id) if data.employee_id is not None else None,
            description=data.description,
            price=data.price,
            is_active=data.is_active
        )
        await self._transaction.commit()
        logger.info("Work updated successfully", work_uuid=str(data.uuid))
