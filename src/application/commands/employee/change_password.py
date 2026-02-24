from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError, PermissionDeniedError
from src.application.keycloak.auth_managers import AdminManager
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee, EmployeeUUID

logger = structlog.get_logger("change_password").bind(service="employee")

ADMIN_CAN_CHANGE = {EmployeePosition.MASTER, EmployeePosition.MANAGER}


@dataclass
class ChangePasswordCommand:
    employee_uuid: UUID
    new_password: str


class ChangePasswordCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        employee_reader: EmployeeReader,
        user_reader: UserReader,
        admin_manager: AdminManager,
    ) -> None:
        self._employee_reader = employee_reader
        self._user_reader = user_reader
        self._admin_manager = admin_manager

    async def run(self, data: ChangePasswordCommand, current_employee: Employee) -> None:
        target = await self._employee_reader.read_by_uuid(EmployeeUUID(data.employee_uuid))
        if not target:
            raise EntityNotFoundError(message=f"Employee {data.employee_uuid} not found")

        caller_pos = current_employee.position
        if caller_pos == EmployeePosition.SUPERVISOR:
            pass
        elif caller_pos == EmployeePosition.ADMIN:
            if target.position not in ADMIN_CAN_CHANGE:
                raise PermissionDeniedError(
                    message="Админ может менять пароль только мастерам и менеджерам.",
                )
        else:
            raise PermissionDeniedError(message="У вас нет прав на смену пароля.")

        user = await self._user_reader.read_by_id(target.user_id)
        if not user:
            raise EntityNotFoundError(message="Linked user not found")

        await self._admin_manager.update_password(str(user.uuid), data.new_password)
        logger.info(
            "Password changed",
            target_uuid=str(data.employee_uuid),
            by=str(current_employee.uuid),
        )
