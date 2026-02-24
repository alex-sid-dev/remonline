"""Устройства: brand_id вместо brand (одна модель — один файл).

Revision ID: add_devices_brand_id
Revises: add_brands_table
Create Date: 2026-02-20

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import BIGINT

revision = "add_devices_brand_id"
down_revision = "add_brands_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("devices", sa.Column("brand_id", BIGINT, nullable=True))
    # Заполняем brand_id: существующие строки — бренд 1 (Прочее); для пустой таблицы ничего не делаем
    op.execute("UPDATE devices SET brand_id = 1 WHERE brand_id IS NULL")
    op.drop_column("devices", "brand")
    op.alter_column(
        "devices",
        "brand_id",
        existing_type=BIGINT,
        nullable=False,
    )
    op.create_foreign_key(
        "fk_devices_brand_id",
        "devices",
        "brands",
        ["brand_id"],
        ["brand_id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_devices_brand_id", "devices", ["brand_id"])


def downgrade() -> None:
    op.add_column("devices", sa.Column("brand", sa.String(100), nullable=True))
    op.drop_index("ix_devices_brand_id", table_name="devices")
    op.drop_constraint("fk_devices_brand_id", "devices", type_="foreignkey")
    op.drop_column("devices", "brand_id")
