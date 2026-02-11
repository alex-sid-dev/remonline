from dataclasses import dataclass
from typing import Optional

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.keycloak.auth_managers import AdminManager, OpenIDManager
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import EmployeeID
from src.entities.employees.services import EmployeeService
from src.entities.users.models import UserUUID

logger = structlog.get_logger("update_employee").bind(service="employee")


@dataclass
class UpdateEmployeeCommand:
    employee_id: int
    access_token: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[EmployeePosition] = None


class UpdateEmployeeCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            entity_saver: EntitySaver,
            admin_manager: AdminManager,
            open_id_manager: OpenIDManager,

            user_reader: UserReader,
            employee_reader: EmployeeReader,

            employee_service: EmployeeService,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._admin_manager = admin_manager
        self._open_id_manager = open_id_manager

        self._user_reader = user_reader
        self._employee_reader = employee_reader

        self._employee_service = employee_service

    async def run(self, data: UpdateEmployeeCommand) -> None:
        await self.verify_token(access_token=data.access_token, open_id_manager=self._open_id_manager)
        user_info = await self._open_id_manager.get_user_info(access_token=data.access_token)
        user = await self._user_reader.read_by_uuid(UserUUID(user_info.user_uuid))
        logger.debug(f"User info: {user.oid}")
        await self.validate_user(user=user)
        employee = await self._employee_reader.read_by_user_oid(user.oid)

        employee_to_update = await self._employee_reader.read_by_oid(EmployeeID(data.employee_id))
        await self.validate_employee_not_found(employee=employee_to_update)
        logger.info(f"Employee info: {employee.position}")
        if employee.position in (EmployeePosition.SUPERVISOR, EmployeePosition.ADMIN):
            employee = self._employee_service.update_employee(
                employee=employee_to_update,
                full_name=data.full_name,
                phone=data.phone,
                position=data.position,
            )
            await self._transaction.commit()
            return None
        return None
