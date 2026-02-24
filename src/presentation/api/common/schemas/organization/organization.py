from uuid import UUID

from pydantic import BaseModel


class OrganizationSchema(BaseModel):
    """Реквизиты организации (создание и редактирование)."""

    name: str = ""
    inn: str = ""
    address: str | None = None
    kpp: str | None = None
    bank_account: str | None = None  # Р/с
    corr_account: str | None = None  # К/с
    bik: str | None = None


class OrganizationResponseSchema(BaseModel):
    """Ответ GET /organization."""

    id: int
    uuid: UUID
    name: str
    inn: str
    address: str | None = None
    kpp: str | None = None
    bank_account: str | None = None
    corr_account: str | None = None
    bik: str | None = None
