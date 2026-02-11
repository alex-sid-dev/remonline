from sqlalchemy import Table, Column, BigInteger, String, Boolean, DateTime, ForeignKey, Float, func, Index
from src.infra.models._base import mapper_registry
from src.entities.works.models import Work

works_table = Table(
    "works",
    mapper_registry.metadata,
    Column("work_id", BigInteger, primary_key=True, autoincrement=True),
    Column("order_id", BigInteger, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False),
    Column("employee_id", BigInteger, ForeignKey("employees.employee_id"), nullable=True),
    Column("title", String(255), nullable=False),
    Column("description", String(1024), nullable=True),
    Column("price", Float, nullable=True),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), server_default=func.now(),
           onupdate=func.now(), nullable=True),
    Index("ix_works_order_id", "order_id"),
)

def map_works_table() -> None:
    mapper_registry.map_imperatively(
        Work,
        works_table,
        properties={
            "oid": works_table.c.work_id,
            "order_oid": works_table.c.order_id,
            "employee_oid": works_table.c.employee_id,
        },
    )
