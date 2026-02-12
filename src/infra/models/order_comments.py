from sqlalchemy import Table, Column, BigInteger, ForeignKey, DateTime, func, UUID, Index, TEXT
from sqlalchemy.orm import relationship

from src.entities.employees.models import Employee
from src.entities.order_comments.models import OrderComment
from src.entities.orders.models import Order
from src.infra.models._base import mapper_registry

order_comments_table = Table(
    "order_comments",
    mapper_registry.metadata,
    Column("order_comment_id", BigInteger, primary_key=True, autoincrement=True),
    Column("order_comment_uuid", UUID(as_uuid=True), nullable=False, unique=True),
    Column("order_id", BigInteger, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False),
    Column("creator_id", BigInteger, ForeignKey("employees.employee_id"), nullable=False),
    Column("comment", TEXT, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Index("ix_order_comments_order_comment_uuid", "order_comment_uuid", unique=True),
)


def map_order_comments_table() -> None:
    mapper_registry.map_imperatively(
        OrderComment,
        order_comments_table,
        properties={
            "id": order_comments_table.c.order_comment_id,
            "uuid": order_comments_table.c.order_comment_uuid,
            "order_id": order_comments_table.c.order_id,
            "creator_id": order_comments_table.c.creator_id,
            "comment": order_comments_table.c.comment,
            "created_at": order_comments_table.c.created_at,

            "creator": relationship(
                Employee,
                lazy="joined",
                innerjoin=True
            ),

            "order": relationship(
                Order,
                lazy="selectin"
            ),
        },
    )
