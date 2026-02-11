from sqlalchemy import Table, Column, BigInteger, String, Float, Boolean, DateTime, func, Index
from src.infra.models._base import mapper_registry
from src.entities.parts.models import Part

parts_table = Table(
    "parts",
    mapper_registry.metadata,
    Column("part_id", BigInteger, primary_key=True, autoincrement=True),
    Column("name", String(255), nullable=False),
    Column("sku", String(100), nullable=True),
    Column("price", Float, nullable=True),
    Column("stock_qty", BigInteger, nullable=True),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), server_default=func.now(),
           onupdate=func.now(), nullable=True),
    Index("ix_parts_sku", "sku", unique=True),
)

def map_parts_table() -> None:
    mapper_registry.map_imperatively(
        Part,
        parts_table,
        properties={
            "oid": parts_table.c.part_id,
        },
    )
