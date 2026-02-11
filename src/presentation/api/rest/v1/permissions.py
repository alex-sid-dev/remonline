from typing import List

import structlog
from dishka.integrations.fastapi import FromDishka

from src.application.errors.auth import UserNotFoundError, InvalidAccessTokenErrorPerm
from src.application.keycloak.auth_managers import OpenIDManager
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.users.models import UserUUID, User
from src.presentation.api.common.dependencies import CredentialsDependency

logger = structlog.getLogger(__name__)


class RoleChecker:
    def __init__(self, list_role: List[EmployeePosition]):
        self.list_role = list_role

    async def __call__(
            self,
            user_reader: FromDishka[UserReader],
            open_id_manager: FromDishka[OpenIDManager],
            employee_reader: FromDishka[EmployeeReader],
            credentials: CredentialsDependency,
    ) -> None:
        await open_id_manager.verify_token(access_token=credentials.credentials)

        user_info = await open_id_manager.get_user_info(access_token=credentials.credentials)
        user = await user_reader.read_by_uuid(UserUUID(user_info.user_uuid))
        logger.debug(f"User info: {user.oid}")
        await self.validate_user(user=user)
        employee = await employee_reader.read_by_user_oid(user.oid)

        if employee.position not in self.list_role:
            raise InvalidAccessTokenErrorPerm()

    @staticmethod
    async def validate_user(user: User) -> None:
        if not user:
            raise UserNotFoundError()
