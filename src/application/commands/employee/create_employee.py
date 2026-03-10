import uuid
from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands._permissions import assert_can_assign_supervisor
from src.application.errors._base import ConflictError
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee
from src.entities.employees.services import EmployeeService
from src.entities.users.models import UserUUID

logger = structlog.get_logger("create_employee").bind(service="employee")


@dataclass(frozen=True, slots=True)
class CreateEmployeeCommandResponse:
    uuid: UUID


@dataclass(frozen=True, slots=True)
class CreateEmployeeCommand:
    user_uuid: UUID
    full_name: str
    phone: str
    position: EmployeePosition
    salary: float | None = None
    profit_percent: float | None = None


class CreateEmployeeCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        employee_service: EmployeeService,
        employee_reader: EmployeeReader,
        user_reader: UserReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._employee_reader = employee_reader
        self._employee_service = employee_service
        self._user_reader = user_reader

    async def run(
        self, data: CreateEmployeeCommand, current_employee: Employee
    ) -> CreateEmployeeCommandResponse:
        if data.position == EmployeePosition.SUPERVISOR:
            assert_can_assign_supervisor(current_employee)

        user = await ensure_exists(
            self._user_reader.read_by_uuid,
            UserUUID(data.user_uuid),
            f"User with uuid {data.user_uuid}",
        )

        existing_employee = await self._employee_reader.read_by_user_id(user.id)
        if existing_employee:
            raise ConflictError(message="Employee already exists for this user")

        employee = self._employee_service.create_employee(
            user_id=user.id,
            uuid=uuid.uuid4(),
            full_name=data.full_name,
            phone=data.phone,
            is_active=True,
            position=data.position,
            organization_id=current_employee.organization_id,
            salary=data.salary,
            profit_percent=data.profit_percent,
        )
        self._entity_saver.add_one(employee)
        await self._transaction.commit()
        logger.info("Employee created successfully", employee_uuid=str(employee.uuid))
        return CreateEmployeeCommandResponse(
            uuid=employee.uuid,
        )
