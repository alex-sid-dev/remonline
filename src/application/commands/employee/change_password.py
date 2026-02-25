from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands._permissions import assert_can_modify_target
from src.application.errors._base import PermissionDeniedError
from src.application.keycloak.auth_managers import AdminManager
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee, EmployeeUUID

logger = structlog.get_logger("change_password").bind(service="employee")


@dataclass(frozen=True, slots=True)
class ChangePasswordCommand:
    employee_uuid: UUID
    new_password: str


class ChangePasswordCommandHandler:
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
        target = await ensure_exists(
            self._employee_reader.read_by_uuid,
            EmployeeUUID(data.employee_uuid),
            f"Employee {data.employee_uuid}",
        )

        caller_pos = current_employee.position
        if caller_pos == EmployeePosition.SUPERVISOR:
            pass
        elif caller_pos == EmployeePosition.ADMIN:
            assert_can_modify_target(current_employee, target)
        else:
            raise PermissionDeniedError(message="У вас нет прав на смену пароля.")

        user = await ensure_exists(
            self._user_reader.read_by_id,
            target.user_id,
            "Linked user",
        )

        await self._admin_manager.update_password(str(user.uuid), data.new_password)
        logger.info(
            "Password changed",
            target_uuid=str(data.employee_uuid),
            by=str(current_employee.uuid),
        )
