from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class OrganizationSchema(BaseModel):
    """Реквизиты организации (создание и редактирование)."""
    name: str = ""
    inn: str = ""
    address: Optional[str] = None
    kpp: Optional[str] = None
    bank_account: Optional[str] = None  # Р/с
    corr_account: Optional[str] = None  # К/с
    bik: Optional[str] = None


class OrganizationResponseSchema(BaseModel):
    """Ответ GET /organization."""
    id: int
    uuid: UUID
    name: str
    inn: str
    address: Optional[str] = None
    kpp: Optional[str] = None
    bank_account: Optional[str] = None
    corr_account: Optional[str] = None
    bik: Optional[str] = None
