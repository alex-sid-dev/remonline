"""Add organizations table (singleton: одна запись).

Revision ID: add_organizations_table
Revises: add_performance_indexes
Create Date: 2026-02-20

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "add_organizations_table"
down_revision = "add_performance_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("organization_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("organization_uuid", UUID(as_uuid=True), nullable=False),
        sa.Column("singleton_key", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("name", sa.String(512), nullable=False, server_default=""),
        sa.Column("inn", sa.String(32), nullable=False, server_default=""),
        sa.Column("address", sa.String(1024), nullable=True),
        sa.Column("kpp", sa.String(32), nullable=True),
        sa.Column("bank_account", sa.String(64), nullable=True),
        sa.Column("corr_account", sa.String(64), nullable=True),
        sa.Column("bik", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("organization_id"),
    )
    op.create_index(
        "ix_organizations_organization_uuid", "organizations", ["organization_uuid"], unique=True
    )
    op.create_index(
        "uq_organizations_singleton_key", "organizations", ["singleton_key"], unique=True
    )


def downgrade() -> None:
    op.drop_index("uq_organizations_singleton_key", table_name="organizations")
    op.drop_index("ix_organizations_organization_uuid", table_name="organizations")
    op.drop_table("organizations")
