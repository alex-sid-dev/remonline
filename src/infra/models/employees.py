from sqlalchemy import Table, Column, BigInteger, ForeignKey, String, Boolean, func, DateTime
from sqlalchemy.orm import relationship

from src.entities.employees.models import Employee
from src.infra.models._base import mapper_registry

employees_table = Table(
    "employees",
    mapper_registry.metadata,
    Column("employee_id", BigInteger, primary_key=True, autoincrement=True),

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

    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)


def map_employee_table() -> None:
    mapper_registry.map_imperatively(
        Employee,
        employees_table,
        properties={
            "oid": employees_table.c.employee_id,
            "user_id": employees_table.c.user_id,
        },
    )
