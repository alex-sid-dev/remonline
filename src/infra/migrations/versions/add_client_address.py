"""Add address column to clients table.

Revision ID: add_client_address
Revises: works_add_qty
Create Date: 2026-02-19
"""

from alembic import op
import sqlalchemy as sa


revision = "add_client_address"
down_revision = "works_add_qty"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("address", sa.String(1024), nullable=True))


def downgrade() -> None:
    op.drop_column("clients", "address")
