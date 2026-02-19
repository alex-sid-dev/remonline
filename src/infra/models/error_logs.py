from sqlalchemy import Table, Column, BigInteger, String, Integer, Text, DateTime, func, Index

from src.infra.models._base import mapper_registry
from src.entities.error_logs.models import ErrorLog

error_logs_table = Table(
    "error_logs",
    mapper_registry.metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("level", String(20), nullable=False),
    Column("error_type", String(255), nullable=False),
    Column("message", Text, nullable=False),
    Column("status_code", Integer, nullable=False),
    Column("path", String(2048), nullable=False),
    Column("method", String(10), nullable=False),
    Column("traceback", Text, nullable=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Index("ix_error_logs_created_at", "created_at"),
    Index("ix_error_logs_level", "level"),
    Index("ix_error_logs_status_code", "status_code"),
)


def map_error_logs_table() -> None:
    mapper_registry.map_imperatively(ErrorLog, error_logs_table)
