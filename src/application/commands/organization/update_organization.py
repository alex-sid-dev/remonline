from dataclasses import dataclass

import structlog
from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.organization_reader import OrganizationReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee
from src.entities.organizations.services import OrganizationService

logger = structlog.get_logger("update_organization").bind(service="organization")


@dataclass
class UpdateOrganizationCommand:
    name: str | None = None
    inn: str | None = None
    address: str | None = None
    kpp: str | None = None
    bank_account: str | None = None
    corr_account: str | None = None
    bik: str | None = None


class UpdateOrganizationCommandHandler(BaseCommandHandler):
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
        data: UpdateOrganizationCommand,
        current_employee: Employee,
    ) -> None:
        org = await self._organization_reader.get_single()
        if not org:
            raise EntityNotFoundError(
                message="Реквизиты организации не заданы. Сначала создайте организацию."
            )
        self._organization_service.update(
            org,
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
        logger.info("Organization updated successfully")
