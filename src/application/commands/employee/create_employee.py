import uuid
from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import ConflictError, EntityNotFoundError, PermissionDeniedError
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee
from src.entities.employees.services import EmployeeService
from src.entities.users.models import UserUUID

logger = structlog.get_logger("create_employee").bind(service="employee")


@dataclass
class CreateEmployeeCommandResponse:
    uuid: UUID


@dataclass
class CreateEmployeeCommand:
    user_uuid: UUID
    full_name: str
    phone: str
    position: EmployeePosition
    salary: float | None = None
    profit_percent: float | None = None


class CreateEmployeeCommandHandler(BaseCommandHandler):
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
        # Только супервизор может создавать сотрудника с ролью supervisor.
        if (
            current_employee.position != EmployeePosition.SUPERVISOR
            and data.position == EmployeePosition.SUPERVISOR
        ):
            raise PermissionDeniedError(
                message="Только супервизор может назначать роль «супервизор»."
            )
        user = await self._user_reader.read_by_uuid(UserUUID(data.user_uuid))
        if not user:
            raise EntityNotFoundError(message=f"User with uuid {data.user_uuid} not found")

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
            salary=data.salary,
            profit_percent=data.profit_percent,
        )
        self._entity_saver.add_one(employee)
        await self._transaction.commit()
        logger.info("Employee created successfully", employee_uuid=str(employee.uuid))
        return CreateEmployeeCommandResponse(
            uuid=employee.uuid,
        )
