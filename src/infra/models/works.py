from sqlalchemy import Table, Column, BigInteger, String, Boolean, DateTime, ForeignKey, Float, func, Index, UUID
from sqlalchemy.orm import relationship

from src.entities.employees.models import Employee
from src.entities.orders.models import Order
from src.infra.models._base import mapper_registry
from src.entities.works.models import Work

works_table = Table(
    "works",
    mapper_registry.metadata,
    Column("work_id", BigInteger, primary_key=True, autoincrement=True),
    Column("work_uuid", UUID(as_uuid=True), nullable=False, unique=True),
    Column("order_id", BigInteger, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False),
    Column("employee_id", BigInteger, ForeignKey("employees.employee_id"), nullable=True),
    Column("title", String(255), nullable=False),
    Column("description", String(1024), nullable=True),
    Column("price", Float, nullable=True),
    Column("qty", BigInteger, nullable=False, server_default="1"),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), server_default=func.now(),
           onupdate=func.now(), nullable=True),
    Index("ix_works_order_id", "order_id"),
    Index("ix_works_work_uuid", "work_uuid", unique=True),
)

def map_works_table() -> None:
    mapper_registry.map_imperatively(
        Work,
        works_table,
        properties={
            "id": works_table.c.work_id,
            "uuid": works_table.c.work_uuid,
            "order_id": works_table.c.order_id,
            "employee_id": works_table.c.employee_id,
            # Связь обратно к заказу
            "order": relationship(Order, back_populates="works"),
            # Автоподгрузка исполнителя работы
            "employee": relationship(Employee, lazy="selectin"),
        },
    )
