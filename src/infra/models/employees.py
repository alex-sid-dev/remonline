from sqlalchemy import (
    UUID,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Table,
    func,
)
from sqlalchemy.orm import relationship

from src.entities.employees.models import Employee
from src.entities.orders.models import Order
from src.infra.models._base import mapper_registry
from src.infra.models.orders import orders_table

employees_table = Table(
    "employees",
    mapper_registry.metadata,
    Column("employee_id", BigInteger, primary_key=True, autoincrement=True),
    Column("employee_uuid", UUID(as_uuid=True), nullable=False, unique=True),
    Column(
        "user_id",
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    ),
    Column("full_name", String(255), nullable=False),
    Column("phone", String(50), nullable=True),
    Column(
        "position",
        String(50),
        nullable=False,
        comment="master | manager | admin | supervisor",
    ),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("organization_id", BigInteger, nullable=False),
    Column("salary", Float, nullable=True),
    Column("profit_percent", Float, nullable=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column(
        "updated_at",
        DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    ),
    Index("ix_employees_employee_uuid", "employee_uuid", unique=True),
    Index("ix_employees_is_active", "is_active"),
    Index(
        "uq_employees_organization_id_phone",
        "organization_id",
        "phone",
        unique=True,
    ),
)


def map_employee_table() -> None:
    mapper_registry.map_imperatively(
        Employee,
        employees_table,
        properties={
            "id": employees_table.c.employee_id,
            "uuid": employees_table.c.employee_uuid,
            "user_id": employees_table.c.user_id,
            "created_orders": relationship(
                Order,
                primaryjoin=employees_table.c.employee_id == orders_table.c.creator_id,
                back_populates="creator",
                viewonly=True,  # Чтобы избежать конфликтов при записи
            ),
            # Заказы, назначенные на сотрудника
            "assigned_orders": relationship(
                Order,
                primaryjoin=employees_table.c.employee_id == orders_table.c.assigned_employee_id,
                back_populates="assigned_employee",
                viewonly=True,
            ),
        },
    )
