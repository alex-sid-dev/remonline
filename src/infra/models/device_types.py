from sqlalchemy import Table, Column, BigInteger, String, Boolean, DateTime, func, Index
from src.entities.device_types.models import DeviceType
from src.infra.models._base import mapper_registry


device_types_table = Table(
    "device_types",
    mapper_registry.metadata,
    Column("device_type_id", BigInteger, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False, unique=True),
    Column("description", String(255), nullable=True),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), server_default=func.now(),
           onupdate=func.now(), nullable=True),
    Index("ix_device_types_name", "name", unique=True),
)

def map_device_types_table() -> None:
    mapper_registry.map_imperatively(
        DeviceType,
        device_types_table,
        properties={
            "oid": device_types_table.c.device_type_id,
        },
    )
