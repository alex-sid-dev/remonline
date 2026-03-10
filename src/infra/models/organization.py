from sqlalchemy import BigInteger, Column, DateTime, String, Table, func
from sqlalchemy.dialects.postgresql import UUID

from src.entities.organizations.models import Organization
from src.infra.models._base import mapper_registry

organizations_table = Table(
    "organizations",
    mapper_registry.metadata,
    Column("organization_id", BigInteger, primary_key=True, autoincrement=True),
    Column("organization_uuid", UUID(as_uuid=True), nullable=False, unique=True),
    Column("name", String(512), nullable=False, server_default=""),
    Column("inn", String(32), nullable=False, server_default=""),
    Column("address", String(1024), nullable=True),
    Column("kpp", String(32), nullable=True),
    Column("bank_account", String(64), nullable=True),  # Р/с
    Column("corr_account", String(64), nullable=True),  # К/с
    Column("bik", String(32), nullable=True),
    Column("owner_user_uuid", UUID(as_uuid=True), nullable=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column(
        "updated_at",
        DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    ),
)


def map_organizations_table() -> None:
    mapper_registry.map_imperatively(
        Organization,
        organizations_table,
        properties={
            "id": organizations_table.c.organization_id,
            "uuid": organizations_table.c.organization_uuid,
        },
    )
