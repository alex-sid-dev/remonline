from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands._permissions import assert_can_modify_target
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee, EmployeeUUID

logger = structlog.get_logger("delete_employee").bind(service="employee")


@dataclass(frozen=True, slots=True)
class DeleteEmployeeCommand:
    uuid: UUID


class DeleteEmployeeCommandHandler:
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
        employee = await ensure_exists(
            self._employee_reader.read_by_uuid, EmployeeUUID(data.uuid),
            f"Employee with uuid {data.uuid}",
        )

        assert_can_modify_target(current_employee, employee)

        await self._entity_saver.delete(employee)
        await self._transaction.commit()
        logger.info("Employee deleted successfully", employee_uuid=str(data.uuid))
