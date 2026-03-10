from sqlalchemy import UUID, BigInteger, Boolean, Column, DateTime, Index, String, Table, func

from src.entities.brands.models import Brand
from src.infra.models._base import mapper_registry

brands_table = Table(
    "brands",
    mapper_registry.metadata,
    Column("brand_id", BigInteger, primary_key=True, autoincrement=True),
    Column("brand_uuid", UUID(as_uuid=True), nullable=False, unique=True),
    Column("name", String(100), nullable=False),
    Column("organization_id", BigInteger, nullable=False),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column(
        "updated_at",
        DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    ),
    Index("ix_brands_name", "name"),
    Index("ix_brands_brand_uuid", "brand_uuid", unique=True),
    Index("ix_brands_organization_id", "organization_id"),
)


def map_brands_table() -> None:
    mapper_registry.map_imperatively(
        Brand,
        brands_table,
        properties={
            "id": brands_table.c.brand_id,
            "uuid": brands_table.c.brand_uuid,
        },
    )
