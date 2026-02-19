"""Create error_logs table.

Revision ID: create_error_logs_table
Revises: drop_unique_serial_number
Create Date: 2026-02-19
"""

from alembic import op
import sqlalchemy as sa


revision = "create_error_logs_table"
down_revision = "drop_unique_serial_number"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "error_logs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("error_type", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("status_code", sa.Integer, nullable=False),
        sa.Column("path", sa.String(2048), nullable=False),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("traceback", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_error_logs_created_at", "error_logs", ["created_at"])
    op.create_index("ix_error_logs_level", "error_logs", ["level"])
    op.create_index("ix_error_logs_status_code", "error_logs", ["status_code"])


def downgrade() -> None:
    op.drop_index("ix_error_logs_status_code", table_name="error_logs")
    op.drop_index("ix_error_logs_level", table_name="error_logs")
    op.drop_index("ix_error_logs_created_at", table_name="error_logs")
    op.drop_table("error_logs")
