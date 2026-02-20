from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.organization_reader import OrganizationReader
from src.entities.employees.models import Employee
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("get_organization").bind(service="organization")


@dataclass
class GetOrganizationResponse:
    id: int
    uuid: UUID
    name: str
    inn: str
    address: Optional[str]
    kpp: Optional[str]
    bank_account: Optional[str]
    corr_account: Optional[str]
    bik: Optional[str]


class GetOrganizationCommandHandler(BaseCommandHandler):
    def __init__(self, organization_reader: OrganizationReader) -> None:
        self._organization_reader = organization_reader

    async def run(self, current_employee: Employee) -> GetOrganizationResponse:
        org = await self._organization_reader.get_single()
        if not org:
            raise EntityNotFoundError(message="Реквизиты организации не заданы")
        return GetOrganizationResponse(
            id=org.id,
            uuid=org.uuid,
            name=org.name,
            inn=org.inn,
            address=org.address,
            kpp=org.kpp,
            bank_account=org.bank_account,
            corr_account=org.corr_account,
            bik=org.bik,
        )
