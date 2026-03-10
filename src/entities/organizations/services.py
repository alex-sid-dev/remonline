from datetime import datetime
from uuid import UUID, uuid4

from src.entities.organizations.models import Organization, OrganizationUUID


class OrganizationService:
    def create(
        self,
        name: str,
        inn: str,
        owner_user_uuid: UUID,
        address: str | None = None,
        kpp: str | None = None,
        bank_account: str | None = None,
        corr_account: str | None = None,
        bik: str | None = None,
    ) -> Organization:
        now = datetime.now()
        return Organization(
            id=None,  # type: ignore
            uuid=OrganizationUUID(uuid4()),
            name=name,
            inn=inn,
            address=address,
            kpp=kpp,
            bank_account=bank_account,
            corr_account=corr_account,
            bik=bik,
            owner_user_uuid=owner_user_uuid,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        org: Organization,
        name: str | None = None,
        inn: str | None = None,
        address: str | None = None,
        kpp: str | None = None,
        bank_account: str | None = None,
        corr_account: str | None = None,
        bik: str | None = None,
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
