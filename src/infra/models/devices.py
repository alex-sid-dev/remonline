from sqlalchemy import Table, Column, BigInteger, String, Boolean, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship

from src.infra.models._base import mapper_registry
from src.entities.devices.models import Device
from src.infra.models.device_types import device_types_table

devices_table = Table(
    "devices",
    mapper_registry.metadata,
    Column("device_id", BigInteger, primary_key=True, autoincrement=True),
    Column("client_id", BigInteger, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False),
    Column("type_id", BigInteger, ForeignKey("device_types.device_type_id"), nullable=False),
    Column("brand", String(100), nullable=False),
    Column("model", String(100), nullable=False),
    Column("serial_number", String(100), nullable=True),
    Column("description", String(1024), nullable=True),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), server_default=func.now(),
           onupdate=func.now(), nullable=True),
    Index("ix_devices_client_id", "client_id"),
    Index("ix_devices_serial_number", "serial_number", unique=True),
)


def map_devices_table() -> None:
    mapper_registry.map_imperatively(
        Device,
        devices_table,
        properties={
            "oid": devices_table.c.device_id,
            "client_oid": devices_table.c.client_id,
            "type_oid": devices_table.c.type_id,

            "type": relationship(
                "DeviceType",
                primaryjoin=devices_table.c.type_id == device_types_table.c.device_type_id,
                lazy="joined",
            ),
        },
    )

