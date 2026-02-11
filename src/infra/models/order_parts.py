from sqlalchemy import Table, Column, BigInteger, Float, ForeignKey, DateTime, func
from src.infra.models._base import mapper_registry
from src.entities.order_parts.models import OrderPart

order_parts_table = Table(
    "order_parts",
    mapper_registry.metadata,
    Column("order_part_id", BigInteger, primary_key=True, autoincrement=True),
    Column("order_id", BigInteger, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False),
    Column("part_id", BigInteger, ForeignKey("parts.part_id", ondelete="CASCADE"), nullable=False),
    Column("qty", BigInteger, nullable=False),
    Column("price", Float, nullable=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)


def map_order_parts_table() -> None:
    mapper_registry.map_imperatively(
        OrderPart,
        order_parts_table,
        properties={
            "oid": order_parts_table.c.order_part_id,
            "order_oid": order_parts_table.c.order_id,
            "part_oid": order_parts_table.c.part_id,
        },
    )
