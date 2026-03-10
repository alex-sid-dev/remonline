from dataclasses import dataclass
from typing import Final
from uuid import UUID, uuid4

import structlog

from src.application.errors.auth import EmailAlreadyExistsError
from src.application.keycloak.auth_managers import AdminManager, OpenIDManager
from src.application.models.auth_token import AuthToken
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.organization_reader import OrganizationReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.application.ports.user_reader import UserReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee
from src.entities.employees.services import EmployeeService
from src.entities.organizations.models import Organization, OrganizationID
from src.entities.organizations.services import OrganizationService
from src.entities.users.services import UserService

logger = structlog.get_logger("register_supervisor").bind(service="auth")


@dataclass(frozen=True, slots=True)
class RegisterSupervisorCommand:
    """
    Command for external supervisor registration.

    Creates:
      - Keycloak user
      - local User
      - Employee with SUPERVISOR position
      - initial Organization record with provided requisites
    """

    email: str
    password: str
    full_name: str
    phone: str
    organization_name: str
    inn: str
    address: str | None = None
    kpp: str | None = None
    bank_account: str | None = None
    corr_account: str | None = None
    bik: str | None = None


@dataclass(frozen=True, slots=True)
class RegisterSupervisorResponse:
    """DTO returned from supervisor registration use case (auth tokens)."""

    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int
    token_type: str
    user_uuid: UUID


class RegisterSupervisorCommandHandler:
    """
    Use case: fully bootstrap a new supervisor "company" from a public endpoint.

    For the current single-tenant model this still assumes a single Organization
    in the system; multi-tenant support will relax this constraint.
    """

    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        admin_manager: AdminManager,
        open_id_manager: OpenIDManager,
        user_reader: UserReader,
        user_service: UserService,
        employee_service: EmployeeService,
        employee_reader: EmployeeReader,
        organization_service: OrganizationService,
        organization_reader: OrganizationReader,
    ) -> None:
        self._transaction: Final = transaction
        self._entity_saver: Final = entity_saver
        self._admin_manager: Final = admin_manager
        self._open_id_manager: Final = open_id_manager
        self._user_reader: Final = user_reader
        self._user_service: Final = user_service
        self._employee_service: Final = employee_service
        self._employee_reader: Final = employee_reader
        self._organization_service: Final = organization_service
        self._organization_reader: Final = organization_reader

    async def run(self, data: RegisterSupervisorCommand) -> RegisterSupervisorResponse:
        logger.info("Supervisor registration started", email=data.email)

        existing_user = await self._user_reader.read_by_email(data.email)
        if existing_user:
            logger.warning("Supervisor registration failed: email already exists", email=data.email)
            raise EmailAlreadyExistsError()

        keycloak_user_uuid: str | None = None

        try:
            keycloak_user_uuid = await self._admin_manager.register_user(
                email=data.email,
                password=data.password,
            )
            logger.info("Keycloak supervisor user registered", email=data.email)

            user = self._user_service.create_user(
                user_uuid=keycloak_user_uuid,
                email=data.email,
            )
            self._entity_saver.add_one(user)
            await self._transaction.flush()

            organization = self._organization_service.create(
                name=data.organization_name,
                inn=data.inn,
                owner_user_uuid=user.uuid,
                address=data.address,
                kpp=data.kpp,
                bank_account=data.bank_account,
                corr_account=data.corr_account,
                bik=data.bik,
            )
            self._entity_saver.add_one(organization)
            await self._transaction.flush()

            employee = self._create_supervisor_employee(
                user_uuid=user.uuid,
                user_id=user.id,
                organization_id=organization.id,  # type: ignore[arg-type]
                full_name=data.full_name,
                phone=data.phone,
            )
            self._entity_saver.add_one(employee)

            await self._transaction.commit()
            logger.info(
                "Supervisor, user and organization persisted",
                email=data.email,
                user_uuid=str(user.uuid),
                employee_uuid=str(employee.uuid),
                organization_uuid=str(organization.uuid),
            )

        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Supervisor registration failed, attempting rollback in Keycloak",
                email=data.email,
                error=str(exc),
            )
            if keycloak_user_uuid:
                try:
                    await self._admin_manager.delete_user(user_uuid=keycloak_user_uuid)
                    logger.info(
                        "Rolled back Keycloak user after supervisor registration failure",
                        user_uuid=keycloak_user_uuid,
                    )
                except Exception as rollback_error:  # noqa: BLE001
                    logger.critical(
                        "ORPHANED SUPERVISOR USER IN KEYCLOAK: manual cleanup required",
                        user_uuid=keycloak_user_uuid,
                        original_error=str(exc),
                        rollback_error=str(rollback_error),
                        exc_info=True,
                    )
            raise

        tokens: AuthToken = await self._open_id_manager.login(email=data.email, password=data.password)
        logger.info("Supervisor logged in after registration", email=data.email)

        return RegisterSupervisorResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_in=tokens.expires_in,
            refresh_expires_in=tokens.refresh_expires_in,
            token_type=tokens.token_type,
            user_uuid=user.uuid,
        )

    def _create_supervisor_employee(
        self,
        user_uuid: str,
        user_id,
        organization_id: OrganizationID,
        full_name: str,
        phone: str,
    ) -> Employee:
        # Ensure no duplicate supervisor employee for this user.
        # (For now system is effectively single-tenant, but the check is cheap.)
        uuid_obj = uuid4()
        logger.info(
            "Creating supervisor employee entity",
            user_uuid=user_uuid,
            employee_uuid=str(uuid_obj),
        )
        return self._employee_service.create_employee(
            user_id=user_id,
            phone=phone,
            full_name=full_name,
            is_active=True,
            position=EmployeePosition.SUPERVISOR,
            uuid=uuid_obj,
            organization_id=organization_id,
        )

