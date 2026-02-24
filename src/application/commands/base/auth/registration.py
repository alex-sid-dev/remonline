import uuid
from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors.auth import EmailAlreadyExistsError
from src.application.keycloak.auth_managers import AdminManager, OpenIDManager
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.application.ports.user_reader import UserReader
from src.entities.users.services import UserService

logger = structlog.get_logger("register").bind(service="auth")


@dataclass(frozen=True, slots=True)
class RegisterCommandResponse:
    uuid: UUID


@dataclass(frozen=True, slots=True)
class RegisterCommand:
    """Command with data required to register a new user."""

    email: str
    password: str


class RegisterCommandHandler(BaseCommandHandler):
    """Use case: register a new user in Keycloak and local database."""

    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        admin_manager: AdminManager,
        user_reader: UserReader,
        user_service: UserService,
        open_id_manager: OpenIDManager,
        employee_reader: EmployeeReader,
    ) -> None:
        self._transaction = transaction
        self._admin_manager = admin_manager
        self._entity_saver = entity_saver
        self._user_reader = user_reader
        self._user_service = user_service
        self._open_id_manager = open_id_manager
        self._employee_reader = employee_reader

    async def run(self, data: RegisterCommand) -> RegisterCommandResponse:
        user = await self._user_reader.read_by_email(data.email)
        if user:
            raise EmailAlreadyExistsError()

        user_uuid: str | None = None

        try:
            user_uuid = await self._admin_manager.register_user(
                email=data.email,
                password=data.password,
            )
            logger.info("Keycloak user registered", email=str(data.email), user_uuid=user_uuid)

            new_user = self._user_service.create_user(
                user_uuid=user_uuid,
                email=data.email,
            )
            self._entity_saver.add_one(new_user)

            await self._transaction.commit()
            logger.info("User persisted in local DB", email=str(data.email), user_uuid=user_uuid)
            return RegisterCommandResponse(uuid=uuid.UUID(user_uuid))

        except Exception as e:
            logger.error(
                "Registration failed, attempting rollback", email=str(data.email), error=str(e)
            )
            if user_uuid:
                try:
                    await self._admin_manager.delete_user(user_uuid=user_uuid)
                    logger.info("Rolled back Keycloak user after DB failure", user_uuid=user_uuid)
                except Exception as rollback_error:
                    logger.critical(
                        "ORPHANED KEYCLOAK USER: failed to delete after registration rollback. "
                        "Manual cleanup required!",
                        user_uuid=user_uuid,
                        original_error=str(e),
                        rollback_error=str(rollback_error),
                        exc_info=True,
                    )
            raise
