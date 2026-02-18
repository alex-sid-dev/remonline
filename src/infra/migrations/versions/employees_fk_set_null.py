"""All FKs to employees: ON DELETE SET NULL

Revision ID: employees_fk_set_null
Revises: orders_assigned_set_null
Create Date: 2026-02-16

So that deleting an employee does not fail when they are referenced
from works, payments, or orders.creator_id.
"""
from alembic import op

revision = "employees_fk_set_null"
down_revision = "orders_assigned_set_null"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # works.employee_id
    op.drop_constraint(
        "fk_works_employee_id_employees",
        "works",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_works_employee_id_employees",
        "works",
        "employees",
        ["employee_id"],
        ["employee_id"],
        ondelete="SET NULL",
    )

    # payments.employee_id
    op.drop_constraint(
        "fk_payments_employee_id_employees",
        "payments",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_payments_employee_id_employees",
        "payments",
        "employees",
        ["employee_id"],
        ["employee_id"],
        ondelete="SET NULL",
    )

    # orders.creator_id
    op.drop_constraint(
        "fk_orders_creator_id_employees",
        "orders",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_orders_creator_id_employees",
        "orders",
        "employees",
        ["creator_id"],
        ["employee_id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_works_employee_id_employees",
        "works",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_works_employee_id_employees",
        "works",
        "employees",
        ["employee_id"],
        ["employee_id"],
    )

    op.drop_constraint(
        "fk_payments_employee_id_employees",
        "payments",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_payments_employee_id_employees",
        "payments",
        "employees",
        ["employee_id"],
        ["employee_id"],
    )

    op.drop_constraint(
        "fk_orders_creator_id_employees",
        "orders",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_orders_creator_id_employees",
        "orders",
        "employees",
        ["creator_id"],
        ["employee_id"],
    )
