import structlog
from src.application.errors._base import EntityNotFoundError
from src.application.ports.organization_reader import OrganizationReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee

logger = structlog.get_logger("delete_organization").bind(service="organization")


class DeleteOrganizationCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        organization_reader: OrganizationReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._organization_reader = organization_reader

    async def run(self, current_employee: Employee) -> None:
        org = await self._organization_reader.get_single()
        if not org:
            raise EntityNotFoundError(message="Реквизиты организации не заданы")
        await self._entity_saver.delete(org)
        await self._transaction.commit()
        logger.info("Organization deleted successfully")
