from dataclasses import dataclass
from typing import List, Optional

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.commands.employee.update_employee import UpdateEmployeeCommand
from src.application.keycloak.auth_managers import AdminManager, OpenIDManager
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee
from src.entities.users.models import UserUUID

logger = structlog.get_logger("read_all_employee").bind(service="employee")


@dataclass
class ReadAllEmployeeCommand:
    access_token: str


@dataclass
class ReadEmployeeResponse:
    full_name: str
    phone: Optional[str]
    position: EmployeePosition

    @classmethod
    def from_entity(cls, entity: Employee) -> "ReadAllEmployeeResponse":
        return cls(
            full_name=entity.full_name,
            phone=entity.phone,
            position=entity.position
        )


class ReadAllEmployeeCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            entity_saver: EntitySaver,
            admin_manager: AdminManager,
            open_id_manager: OpenIDManager,

            user_reader: UserReader,
            employee_reader: EmployeeReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._admin_manager = admin_manager
        self._open_id_manager = open_id_manager

        self._user_reader = user_reader
        self._employee_reader = employee_reader

    async def run(self, data: ReadAllEmployeeCommand) -> List[ReadEmployeeResponse] | None:
        await self.verify_token(access_token=data.access_token, open_id_manager=self._open_id_manager)
        user_info = await self._open_id_manager.get_user_info(access_token=data.access_token)
        user = await self._user_reader.read_by_uuid(UserUUID(user_info.user_uuid))
        logger.debug(f"User info: {user.oid}")
        await self.validate_user(user=user)
        employee = await self._employee_reader.read_by_user_oid(user.oid)
        if employee.position in (EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN):
            employees = await self._employee_reader.read_all_active()
            response = [
                ReadEmployeeResponse.from_entity(emp)
                for emp in employees if emp is not None
            ]
            return response
        return None
