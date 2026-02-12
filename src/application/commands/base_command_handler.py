from abc import ABC
import structlog

from src.application.errors.employee import EmployeeNotFoundError, EmployeeIsAlreadyExist
from src.entities.employees.models import Employee
from src.entities.users.models import User
from src.application.errors.auth import TokenInvalidError, UserNotFoundError, EmailAlreadyExistsError

logger = structlog.getLogger(__name__)


class BaseCommandHandler(ABC):
    @staticmethod
    async def verify_token(access_token: str, open_id_manager) -> None:
        """Единый метод проверки токена для всех наследников"""
        try:
            await open_id_manager.verify_token(access_token=access_token)
        except Exception:
            logger.exception("Failed to verify access token")
            raise TokenInvalidError()

    @staticmethod
    async def validate_user(user: User) -> None:
        if not user:
            raise UserNotFoundError()

    @staticmethod
    async def validate_user_already_exist(user: User) -> None:
        if user:
            raise EmailAlreadyExistsError()

    @staticmethod
    async def validate_employee_not_found(employee: Employee) -> None:
        if employee is None:
            raise EmployeeNotFoundError()

    @staticmethod
    async def validate_employee_already_exist(employee: Employee) -> None:
        if employee:
            raise EmployeeIsAlreadyExist()
