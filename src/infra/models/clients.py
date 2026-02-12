from sqlalchemy import Table, Column, BigInteger, String, Boolean, DateTime, func, Index, UUID
from src.infra.models._base import mapper_registry
from src.entities.clients.models import Client

clients_table = Table(
    "clients",
    mapper_registry.metadata,
    Column("client_id", BigInteger, primary_key=True, autoincrement=True),
    Column("client_uuid", UUID(as_uuid=True), nullable=False, unique=True),
    Column("full_name", String(255), nullable=False),
    Column("phone", String(50), nullable=False),
    Column("email", String(255), nullable=True),
    Column("telegram_nick", String(255), nullable=True),
    Column("comment", String(1024), nullable=True),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), server_default=func.now(),
           onupdate=func.now(), nullable=True),
    Index("ix_clients_phone", "phone"),
    Index("ix_clients_email", "email"),
    Index("ix_clients_client_uuid", "client_uuid", unique=True),
)


def map_clients_table() -> None:
    mapper_registry.map_imperatively(
        Client,
        clients_table,
        properties={
            "id": clients_table.c.client_id,
            "uuid": clients_table.c.client_uuid,
        },
    )
