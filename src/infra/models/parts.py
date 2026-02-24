from sqlalchemy import (
    UUID,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    String,
    Table,
    func,
)

from src.entities.parts.models import Part
from src.infra.models._base import mapper_registry

parts_table = Table(
    "parts",
    mapper_registry.metadata,
    Column("part_id", BigInteger, primary_key=True, autoincrement=True),
    Column("part_uuid", UUID(as_uuid=True), nullable=False, unique=True),
    Column("name", String(255), nullable=False),
    Column("sku", String(100), nullable=True),
    Column("price", Float, nullable=True),
    Column("stock_qty", BigInteger, nullable=True),
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
    Index("ix_parts_sku", "sku", unique=True),
    Index("ix_parts_part_uuid", "part_uuid", unique=True),
)


def map_parts_table() -> None:
    mapper_registry.map_imperatively(
        Part,
        parts_table,
        properties={
            "id": parts_table.c.part_id,
            "uuid": parts_table.c.part_uuid,
            "name": parts_table.c.name,
            "sku": parts_table.c.sku,
            "price": parts_table.c.price,
            "stock_qty": parts_table.c.stock_qty,
            "is_active": parts_table.c.is_active,
        },
    )
