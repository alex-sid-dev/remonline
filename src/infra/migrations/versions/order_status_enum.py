"""Restrict orders.status to enum-like set of values.

Revision ID: orders_status_enum
Revises: employees_fk_set_null
Create Date: 2026-02-16

This migration aligns the database with the Python OrderStatus enum:

    NEW = "new"                       # новый
    ACCEPTED = "accepted"             # принят в работу
    DIAGNOSTICS = "diagnostics"       # на диагностике
    ON_APPROVAL = "on_approval"       # на согласовании
    WAITING_PARTS = "waiting_parts"   # ждем запчасти
    IN_REPAIR = "in_repair"           # в ремонте
    PAID = "paid"                     # оплачен
    CLOSED = "closed"                 # закрыт
    REJECTED = "rejected"             # отказ
"""

from alembic import op

revision = "orders_status_enum"
down_revision = "employees_fk_set_null"
branch_labels = None
depends_on = None


STATUS_VALUES = [
    "new",
    "accepted",
    "diagnostics",
    "on_approval",
    "waiting_parts",
    "in_repair",
    "paid",
    "closed",
    "rejected",
]


def upgrade() -> None:
    # На всякий случай приводим старые/нестандартные значения к 'new',
    # чтобы CHECK‑constraint не упал на существующих данных.
    allowed_values_sql = ", ".join(f"'{v}'" for v in STATUS_VALUES)
    op.execute(
        f"""
        UPDATE orders
        SET status = 'new'
        WHERE status NOT IN ({allowed_values_sql})
           OR status IS NULL;
        """,
    )

    # Добавляем CHECK‑constraint, который ограничивает статусы набором из enum.
    op.create_check_constraint(
        "ck_orders_status_enum",
        "orders",
        f"status IN ({allowed_values_sql})",
    )


def downgrade() -> None:
    # Убираем ограничение, сами значения в колонке не трогаем.
    op.drop_constraint(
        "ck_orders_status_enum",
        "orders",
        type_="check",
    )
