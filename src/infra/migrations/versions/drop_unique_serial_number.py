"""Drop unique constraint on devices.serial_number.

Revision ID: drop_unique_serial_number
Revises: add_client_address
Create Date: 2026-02-19
"""

from alembic import op

revision = "drop_unique_serial_number"
down_revision = "add_client_address"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_devices_serial_number", table_name="devices")
    op.create_index("ix_devices_serial_number", "devices", ["serial_number"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_devices_serial_number", table_name="devices")
    op.create_index("ix_devices_serial_number", "devices", ["serial_number"], unique=True)
