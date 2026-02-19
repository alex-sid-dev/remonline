"""Add performance indexes for frequently queried columns.

Revision ID: add_performance_indexes
Revises: add_employee_salary_fields
Create Date: 2026-02-19
"""

from alembic import op

revision = "add_performance_indexes"
down_revision = "add_employee_salary_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_is_active", "orders", ["is_active"])
    op.create_index("ix_orders_is_active_created_at", "orders", ["is_active", "created_at"])
    op.create_index("ix_employees_is_active", "employees", ["is_active"])
    op.create_index("ix_clients_is_active", "clients", ["is_active"])
    op.create_index("ix_order_comments_order_id", "order_comments", ["order_id"])
    op.create_index("ix_order_parts_order_id", "order_parts", ["order_id"])
    op.create_index("ix_works_employee_id", "works", ["employee_id"])


def downgrade() -> None:
    op.drop_index("ix_works_employee_id", "works")
    op.drop_index("ix_order_parts_order_id", "order_parts")
    op.drop_index("ix_order_comments_order_id", "order_comments")
    op.drop_index("ix_clients_is_active", "clients")
    op.drop_index("ix_employees_is_active", "employees")
    op.drop_index("ix_orders_is_active_created_at", "orders")
    op.drop_index("ix_orders_is_active", "orders")
    op.drop_index("ix_orders_status", "orders")
