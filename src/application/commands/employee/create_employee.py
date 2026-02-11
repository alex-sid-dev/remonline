from dataclasses import dataclass

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.keycloak.auth_managers import AdminManager, OpenIDManager
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import EmployeeID
from src.entities.employees.services import EmployeeService
from src.entities.users.models import UserUUID, UserID

logger = structlog.get_logger("create_employee").bind(service="employee")


@dataclass
class CreateEmployeeCommand:
    user_id: int
    full_name: str
    phone: str
    access_token: str
    position: EmployeePosition


class CreateEmployeeCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            entity_saver: EntitySaver,
            admin_manager: AdminManager,
            user_reader: UserReader,
            open_id_manager: OpenIDManager,
            employee_service: EmployeeService,
            employee_reader: EmployeeReader,

    ) -> None:
        self._transaction = transaction
        self._admin_manager = admin_manager
        self._entity_saver = entity_saver
        self._user_reader = user_reader
        self._open_id_manager = open_id_manager
        self._employee_reader = employee_reader
        self._employee_service = employee_service

    async def run(self, data: CreateEmployeeCommand) -> None:
        await self.verify_token(access_token=data.access_token, open_id_manager=self._open_id_manager)
        user_info = await self._open_id_manager.get_user_info(access_token=data.access_token)
        user = await self._user_reader.read_by_uuid(UserUUID(user_info.user_uuid))
        logger.debug(f"User info: {user.oid}")
        await self.validate_user(user=user)
        employee = await self._employee_reader.read_by_user_oid(user.oid)
        new_employee = await self._employee_reader.read_by_user_oid(UserID(data.user_id))
        await self.validate_employee_already_exist(employee=new_employee)
        if employee.position in (EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN):
            employee = self._employee_service.create_employee(
                user_id=UserID(data.user_id),
                full_name=data.full_name,
                phone=data.phone,
                is_active=True,
                position=data.position
            )
            self._entity_saver.add_one(employee)
            await self._transaction.commit()
            return None
        return None