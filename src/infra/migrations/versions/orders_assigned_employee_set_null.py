"""orders.assigned_employee_id: ON DELETE SET NULL

Revision ID: orders_assigned_set_null
Revises: add_order_comments_table
Create Date: 2026-02-16

When an employee is deleted, orders that had them as assigned_employee_id
will get assigned_employee_id = NULL instead of blocking the delete.
"""
from alembic import op

revision = "orders_assigned_set_null"
down_revision = "add_order_comments_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop FK and recreate with ON DELETE SET NULL (so deleting an employee sets assigned_employee_id to NULL in orders).
    op.drop_constraint(
        "fk_orders_assigned_employee_id_employees",
        "orders",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_orders_assigned_employee_id_employees",
        "orders",
        "employees",
        ["assigned_employee_id"],
        ["employee_id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_orders_assigned_employee_id_employees",
        "orders",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_orders_assigned_employee_id_employees",
        "orders",
        "employees",
        ["assigned_employee_id"],
        ["employee_id"],
    )
