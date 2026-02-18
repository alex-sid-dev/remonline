"""Add qty column to works table.

Revision ID: works_add_qty
Revises: orders_status_enum_fix
Create Date: 2026-02-18
"""

from alembic import op
import sqlalchemy as sa


revision = "works_add_qty"
down_revision = "orders_status_enum_fix"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем столбец qty с дефолтом 1 для уже существующих работ.
    op.add_column(
        "works",
        sa.Column("qty", sa.BigInteger(), nullable=True),
    )
    op.execute("UPDATE works SET qty = 1 WHERE qty IS NULL;")
    op.alter_column("works", "qty", nullable=False)


def downgrade() -> None:
    op.drop_column("works", "qty")

