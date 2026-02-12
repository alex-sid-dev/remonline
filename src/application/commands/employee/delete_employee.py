from dataclasses import dataclass
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.employees.models import Employee, EmployeeUUID
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("delete_employee").bind(service="employee")

@dataclass
class DeleteEmployeeCommand:
    uuid: UUID

class DeleteEmployeeCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            entity_saver: EntitySaver,
            employee_reader: EmployeeReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._employee_reader = employee_reader

    async def run(self, data: DeleteEmployeeCommand, current_employee: Employee) -> None:
        employee = await self._employee_reader.read_by_uuid(EmployeeUUID(data.uuid))
        if not employee:
            raise EntityNotFoundError(f"Employee with uuid {data.uuid} not found")
            
        await self._entity_saver.delete(employee)
        await self._transaction.commit()
        logger.info("Employee deleted successfully", employee_uuid=str(data.uuid))
