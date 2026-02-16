from sqlalchemy import Table, Column, BigInteger, Float, ForeignKey, DateTime, func, UUID, Index
from sqlalchemy.orm import relationship

from src.entities.orders.models import Order
from src.entities.parts.models import Part
from src.infra.models._base import mapper_registry
from src.entities.order_parts.models import OrderPart

order_parts_table = Table(
    "order_parts",
    mapper_registry.metadata,
    Column("order_part_id", BigInteger, primary_key=True, autoincrement=True),
    Column("order_part_uuid", UUID(as_uuid=True), nullable=False, unique=True),
    Column("order_id", BigInteger, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False),
    Column("part_id", BigInteger, ForeignKey("parts.part_id", ondelete="CASCADE"), nullable=False),
    Column("qty", BigInteger, nullable=False),
    Column("price", Float, nullable=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Index("ix_order_parts_order_part_uuid", "order_part_uuid", unique=True),
)


def map_order_parts_table() -> None:
    mapper_registry.map_imperatively(
        OrderPart,
        order_parts_table,
        properties={
            "id": order_parts_table.c.order_part_id,
            "uuid": order_parts_table.c.order_part_uuid,
            "order_id": order_parts_table.c.order_id,
            "part_id": order_parts_table.c.part_id,
            "qty": order_parts_table.c.qty,
            "price": order_parts_table.c.price,

            # Автоподгрузка информации о запчасти из справочника
            "part_info": relationship(Part, lazy="selectin"),
            "order": relationship(Order, back_populates="parts"),
        },
    )
