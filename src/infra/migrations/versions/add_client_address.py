"""Add address column to clients table.

Revision ID: add_client_address
Revises: works_add_qty
Create Date: 2026-02-19
"""

import sqlalchemy as sa
from alembic import op

revision = "add_client_address"
down_revision = "works_add_qty"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("address", sa.String(1024), nullable=True))


def downgrade() -> None:
    op.drop_column("clients", "address")
