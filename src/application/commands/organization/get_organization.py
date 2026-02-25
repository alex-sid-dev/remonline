from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict
from src.application.errors._base import EntityNotFoundError
from src.application.ports.organization_reader import OrganizationReader
from src.entities.employees.models import Employee

logger = structlog.get_logger("get_organization").bind(service="organization")


class GetOrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID
    name: str
    inn: str
    address: str | None = None
    kpp: str | None = None
    bank_account: str | None = None
    corr_account: str | None = None
    bik: str | None = None


class GetOrganizationCommandHandler:
    def __init__(self, organization_reader: OrganizationReader) -> None:
        self._organization_reader = organization_reader

    async def run(self, current_employee: Employee) -> GetOrganizationResponse:
        org = await self._organization_reader.get_single()
        if not org:
            raise EntityNotFoundError(message="Реквизиты организации не заданы")
        return GetOrganizationResponse.model_validate(org)
