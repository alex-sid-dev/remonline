"""Drop legacy check constraint on orders.status that conflicts with new enum rules.

Revision ID: orders_status_enum_fix
Revises: orders_status_enum
Create Date: 2026-02-18
"""

from alembic import op


revision = "orders_status_enum_fix"
down_revision = "orders_status_enum"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # В старой версии миграции/схемы могла остаться проверка
    # с другим именем и другим набором значений. Удаляем её,
    # если она существует, чтобы не мешала актуальному enum‑набору.
    op.execute(
        "ALTER TABLE orders DROP CONSTRAINT IF EXISTS ck_orders_ck_orders_status_enum;",
    )


def downgrade() -> None:
    # Откат — просто ничего не делаем, старый констрейнт не восстанавливаем.
    pass

