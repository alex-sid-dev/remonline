"""Таблица брендов (одна модель — один файл миграции).

Revision ID: add_brands_table
Revises: add_organizations_table
Create Date: 2026-02-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, BIGINT, BOOLEAN, TIMESTAMP

revision = "add_brands_table"
down_revision = "add_organizations_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "brands",
        sa.Column("brand_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("brand_uuid", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_active", BOOLEAN, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()),
    )
    op.create_index("ix_brands_name", "brands", ["name"])
    op.create_index("ix_brands_brand_uuid", "brands", ["brand_uuid"], unique=True)
    # Бренд по умолчанию для миграции devices.brand -> devices.brand_id
    op.execute(
        "INSERT INTO brands (brand_id, brand_uuid, name, is_active, created_at, updated_at) "
        "VALUES (1, gen_random_uuid(), 'Прочее', true, now(), now())"
    )
    # Иначе следующий INSERT без brand_id получит 1 из sequence → duplicate key
    op.execute(
        "SELECT setval(pg_get_serial_sequence('brands', 'brand_id'), (SELECT COALESCE(MAX(brand_id), 1) FROM brands))"
    )


def downgrade() -> None:
    op.drop_index("ix_brands_brand_uuid", table_name="brands")
    op.drop_index("ix_brands_name", table_name="brands")
    op.drop_table("brands")
