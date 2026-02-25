from dataclasses import dataclass
from uuid import UUID

import structlog
from src.application.errors._base import ConflictError
from src.application.ports.organization_reader import OrganizationReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee
from src.entities.organizations.services import OrganizationService

logger = structlog.get_logger("create_organization").bind(service="organization")


@dataclass(frozen=True, slots=True)
class CreateOrganizationCommand:
    name: str
    inn: str
    address: str | None = None
    kpp: str | None = None
    bank_account: str | None = None
    corr_account: str | None = None
    bik: str | None = None


@dataclass(frozen=True, slots=True)
class CreateOrganizationCommandResponse:
    uuid: UUID


class CreateOrganizationCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        organization_service: OrganizationService,
        organization_reader: OrganizationReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._organization_service = organization_service
        self._organization_reader = organization_reader

    async def run(
        self,
        data: CreateOrganizationCommand,
        current_employee: Employee,
    ) -> CreateOrganizationCommandResponse:
        existing = await self._organization_reader.get_single()
        if existing:
            raise ConflictError(message="Организация уже задана. Используйте редактирование.")
        org = self._organization_service.create(
            name=data.name,
            inn=data.inn,
            address=data.address,
            kpp=data.kpp,
            bank_account=data.bank_account,
            corr_account=data.corr_account,
            bik=data.bik,
        )
        self._entity_saver.add_one(org)
        await self._transaction.commit()
        logger.info("Organization created successfully", organization_uuid=str(org.uuid))
        return CreateOrganizationCommandResponse(uuid=org.uuid)
