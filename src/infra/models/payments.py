from sqlalchemy import Table, Column, BigInteger, Float, String, DateTime, ForeignKey, func, Index, UUID
from src.infra.models._base import mapper_registry
from src.entities.payments.models import Payment

payments_table = Table(
    "payments",
    mapper_registry.metadata,
    Column("payment_id", BigInteger, primary_key=True, autoincrement=True),
    Column("payment_uuid", UUID(as_uuid=True), nullable=False, unique=True),
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
    Index("ix_payments_payment_uuid", "payment_uuid", unique=True),
)


def map_payments_table() -> None:
    mapper_registry.map_imperatively(
        Payment,
        payments_table,
        properties={
            "id": payments_table.c.payment_id,
            "uuid": payments_table.c.payment_uuid,
            "order_id": payments_table.c.order_id,
            "employee_id": payments_table.c.employee_id,
        },
    )
