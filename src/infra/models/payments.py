from sqlalchemy import Table, Column, BigInteger, Float, String, DateTime, ForeignKey, func, Index
from src.infra.models._base import mapper_registry
from src.entities.payments.models import Payment

payments_table = Table(
    "payments",
    mapper_registry.metadata,
    Column("payment_id", BigInteger, primary_key=True, autoincrement=True),
    Column("order_id", BigInteger, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False),
    Column("employee_id", BigInteger, ForeignKey("employees.employee_id"), nullable=True),
    Column("amount", Float, nullable=False),
    Column("payment_method", String(50), nullable=False),
    Column("comment", String(1024), nullable=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), server_default=func.now(),
           onupdate=func.now(), nullable=True),
    # индекс можно добавить на order_id для быстрого поиска платежей по заказу
    Index("ix_payments_order_id", "order_id"),
)


def map_payments_table() -> None:
    mapper_registry.map_imperatively(
        Payment,
        payments_table,
        properties={
            "oid": payments_table.c.payment_id,
            "order_oid": payments_table.c.order_id,
            "employee_oid": payments_table.c.employee_id,
        },
    )
