from sqlalchemy import Table, Column, BigInteger, String, Boolean, DateTime, ForeignKey, Float, func, Index, UUID
from sqlalchemy.orm import relationship

from src.entities.order_comments.models import OrderComment
from src.infra.models._base import mapper_registry
from src.entities.orders.models import Order

orders_table = Table(
    "orders",
    mapper_registry.metadata,
    Column("order_id", BigInteger, primary_key=True, autoincrement=True),
    Column("order_uuid", UUID(as_uuid=True), nullable=False, unique=True),
    Column("client_id", BigInteger, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False),
    Column("device_id", BigInteger, ForeignKey("devices.device_id", ondelete="CASCADE"), nullable=False),
    Column("creator_id", BigInteger, ForeignKey("employees.employee_id"), nullable=True),
    Column("assigned_employee_id", BigInteger, ForeignKey("employees.employee_id"), nullable=True),
    Column("status", String(50), nullable=False, server_default="new"),
    Column("problem_description", String(1024), nullable=True),
    Column("comment", String(1024), nullable=True),
    Column("price", Float, nullable=True),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), server_default=func.now(),
           onupdate=func.now(), nullable=True),
    Index("ix_orders_client_id", "client_id"),
    Index("ix_orders_device_id", "device_id"),
    Index("ix_orders_order_uuid", "order_uuid", unique=True),
)


def map_orders_table() -> None:
    mapper_registry.map_imperatively(
        Order,
        orders_table,
        properties={
            "id": orders_table.c.order_id,
            "uuid": orders_table.c.order_uuid,
            "client_id": orders_table.c.client_id,
            "device_id": orders_table.c.device_id,
            "creator_id": orders_table.c.creator_id,
            "assigned_employee_id": orders_table.c.assigned_employee_id,

            "comments": relationship(
                OrderComment,
                back_populates="order",
                cascade="all, delete-orphan",
                lazy="selectin"
            )
        },
    )
