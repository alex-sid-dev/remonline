from datetime import datetime
from typing import Optional
from uuid import uuid4

from src.entities.organizations.models import Organization, OrganizationID, OrganizationUUID


class OrganizationService:
    def create(
        self,
        name: str,
        inn: str,
        address: Optional[str] = None,
        kpp: Optional[str] = None,
        bank_account: Optional[str] = None,
        corr_account: Optional[str] = None,
        bik: Optional[str] = None,
    ) -> Organization:
        now = datetime.now()
        return Organization(
            id=None,  # type: ignore
            uuid=OrganizationUUID(uuid4()),
            singleton_key=1,
            name=name,
            inn=inn,
            address=address,
            kpp=kpp,
            bank_account=bank_account,
            corr_account=corr_account,
            bik=bik,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        org: Organization,
        name: Optional[str] = None,
        inn: Optional[str] = None,
        address: Optional[str] = None,
        kpp: Optional[str] = None,
        bank_account: Optional[str] = None,
        corr_account: Optional[str] = None,
        bik: Optional[str] = None,
    ) -> Organization:
        if name is not None:
            org.name = name
        if inn is not None:
            org.inn = inn
        if address is not None:
            org.address = address
        if kpp is not None:
            org.kpp = kpp
        if bank_account is not None:
            org.bank_account = bank_account
        if corr_account is not None:
            org.corr_account = corr_account
        if bik is not None:
            org.bik = bik
        org.updated_at = datetime.now()
        return org
