"""create device, order, part tables with updated_at triggers

Revision ID: devices_orders_parts
Revises: full_postgres_migration
Create Date: 2026-02-05 13:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import BIGINT, BOOLEAN, TIMESTAMP, UUID

# revision identifiers, used by Alembic.
revision = "devices_orders_parts"
down_revision = "full_postgres_migration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Device Types ---
    op.create_table(
        "device_types",
        sa.Column("device_type_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("device_type_uuid", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("is_active", BOOLEAN, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_device_types_name", "device_types", ["name"], unique=True)
    op.create_index(
        "ix_device_types_device_type_uuid", "device_types", ["device_type_uuid"], unique=True
    )

    # --- Devices ---
    op.create_table(
        "devices",
        sa.Column("device_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("device_uuid", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column(
            "client_id",
            BIGINT,
            sa.ForeignKey("clients.client_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type_id", BIGINT, sa.ForeignKey("device_types.device_type_id"), nullable=False),
        sa.Column("brand", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("is_active", BOOLEAN, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_devices_client_id", "devices", ["client_id"])
    op.create_index("ix_devices_serial_number", "devices", ["serial_number"], unique=True)
    op.create_index("ix_devices_device_uuid", "devices", ["device_uuid"], unique=True)

    # --- Parts ---
    op.create_table(
        "parts",
        sa.Column("part_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("part_uuid", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sku", sa.String(100), nullable=True),
        sa.Column("price", sa.Float, nullable=True),
        sa.Column("stock_qty", BIGINT, nullable=True),
        sa.Column("is_active", BOOLEAN, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_parts_sku", "parts", ["sku"], unique=True)
    op.create_index("ix_parts_part_uuid", "parts", ["part_uuid"], unique=True)

    # --- Orders ---
    op.create_table(
        "orders",
        sa.Column("order_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("order_uuid", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column(
            "client_id",
            BIGINT,
            sa.ForeignKey("clients.client_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "device_id",
            BIGINT,
            sa.ForeignKey("devices.device_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("creator_id", BIGINT, sa.ForeignKey("employees.employee_id"), nullable=True),
        sa.Column(
            "assigned_employee_id", BIGINT, sa.ForeignKey("employees.employee_id"), nullable=True
        ),
        sa.Column("status", sa.String(50), nullable=False, server_default="new"),
        sa.Column("problem_description", sa.String(1024), nullable=True),
        sa.Column("comment", sa.String(1024), nullable=True),
        sa.Column("price", sa.Float, nullable=True),
        sa.Column("is_active", BOOLEAN, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_orders_client_id", "orders", ["client_id"])
    op.create_index("ix_orders_device_id", "orders", ["device_id"])
    op.create_index("ix_orders_order_uuid", "orders", ["order_uuid"], unique=True)

    # --- Order Parts ---
    op.create_table(
        "order_parts",
        sa.Column("order_part_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("order_part_uuid", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column(
            "order_id", BIGINT, sa.ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "part_id", BIGINT, sa.ForeignKey("parts.part_id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("qty", BIGINT, nullable=False),
        sa.Column("price", sa.Float, nullable=True),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_order_parts_order_part_uuid", "order_parts", ["order_part_uuid"], unique=True
    )

    # --- Payments ---
    op.create_table(
        "payments",
        sa.Column("payment_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("payment_uuid", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column(
            "order_id", BIGINT, sa.ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("employee_id", BIGINT, sa.ForeignKey("employees.employee_id"), nullable=True),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=False),
        sa.Column("comment", sa.String(1024), nullable=True),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_payments_order_id", "payments", ["order_id"])
    op.create_index("ix_payments_payment_uuid", "payments", ["payment_uuid"], unique=True)

    # --- Works ---
    op.create_table(
        "works",
        sa.Column("work_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("work_uuid", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column(
            "order_id", BIGINT, sa.ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("employee_id", BIGINT, sa.ForeignKey("employees.employee_id"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("price", sa.Float, nullable=True),
        sa.Column("is_active", BOOLEAN, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_works_order_id", "works", ["order_id"])
    op.create_index("ix_works_work_uuid", "works", ["work_uuid"], unique=True)

    # --- Trigger function for updated_at ---
    op.execute("""
               CREATE
               OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
               BEGIN
        NEW.updated_at
               = now();
               RETURN NEW;
               END;
    $$
               LANGUAGE 'plpgsql';
               """)

    # --- Attach trigger to tables with updated_at ---
    for table in ["device_types", "devices", "parts", "orders", "payments", "works"]:
        op.execute(f"""
        CREATE TRIGGER {table}_updated_at_trigger
        BEFORE UPDATE ON {table}
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers
    for table in ["works", "payments", "orders", "order_parts", "devices", "device_types", "parts"]:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_updated_at_trigger ON {table};")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop tables in reverse dependency order
    op.drop_index("ix_works_order_id", table_name="works")
    op.drop_table("works")

    op.drop_index("ix_payments_order_id", table_name="payments")
    op.drop_table("payments")

    op.drop_table("order_parts")

    op.drop_index("ix_orders_device_id", table_name="orders")
    op.drop_index("ix_orders_client_id", table_name="orders")
    op.drop_table("orders")

    op.drop_index("ix_devices_serial_number", table_name="devices")
    op.drop_index("ix_devices_client_id", table_name="devices")
    op.drop_table("devices")

    op.drop_index("ix_device_types_name", table_name="device_types")
    op.drop_table("device_types")

    op.drop_index("ix_parts_sku", table_name="parts")
    op.drop_table("parts")
