"""Add salary and profit_percent columns to employees table.

Revision ID: add_employee_salary_fields
Revises: create_error_logs_table
Create Date: 2026-02-19
"""

import sqlalchemy as sa
from alembic import op

revision = "add_employee_salary_fields"
down_revision = "create_error_logs_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("salary", sa.Float, nullable=True))
    op.add_column("employees", sa.Column("profit_percent", sa.Float, nullable=True))


def downgrade() -> None:
    op.drop_column("employees", "profit_percent")
    op.drop_column("employees", "salary")
