"""Add organization_id to core tables and make organizations multi-tenant.

Revision ID: multitenant_organizations
Revises: add_devices_brand_id
Create Date: 2026-03-06
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


revision = "multitenant_organizations"
down_revision = "add_devices_brand_id"
branch_labels = None
depends_on = None


def _get_or_create_default_org_id() -> int:
    conn = op.get_bind()
    org_id = conn.execute(sa.text("SELECT organization_id FROM organizations LIMIT 1")).scalar()
    if org_id is not None:
        return int(org_id)

    new_uuid = uuid.uuid4()
    org_id = conn.execute(
        sa.text(
            "INSERT INTO organizations (organization_uuid, name, inn) "
            "VALUES (:uuid, '', '') RETURNING organization_id"
        ),
        {"uuid": str(new_uuid)},
    ).scalar_one()
    return int(org_id)


def upgrade() -> None:
    conn = op.get_bind()

    # organizations: drop singleton_key and add owner_user_uuid
    with op.batch_alter_table("organizations") as batch:
        batch.add_column(sa.Column("owner_user_uuid", PG_UUID(as_uuid=True), nullable=True))
        # В старой схеме мог существовать уникальный индекс по singleton_key
        batch.drop_index("uq_organizations_singleton_key")
        batch.drop_column("singleton_key")

    # Новые колонки organization_id
    op.add_column(
        "employees",
        sa.Column("organization_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "clients",
        sa.Column("organization_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "devices",
        sa.Column("organization_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("organization_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "parts",
        sa.Column("organization_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "brands",
        sa.Column("organization_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "device_types",
        sa.Column("organization_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "payments",
        sa.Column("organization_id", sa.BigInteger(), nullable=True),
    )

    org_id = _get_or_create_default_org_id()

    # Заполняем новой организацией все существующие данные.
    for table in (
        "employees",
        "clients",
        "devices",
        "orders",
        "parts",
        "brands",
        "device_types",
        "payments",
    ):
        conn.execute(
            sa.text(f"UPDATE {table} SET organization_id = :org_id WHERE organization_id IS NULL"),
            {"org_id": org_id},
        )

    # Делаем organization_id NOT NULL и добавляем индексы.
    with op.batch_alter_table("employees") as batch:
        batch.alter_column("organization_id", nullable=False)
        batch.create_index("ix_employees_organization_id", ["organization_id"])
        batch.create_foreign_key(
            "fk_employees_organization_id_organizations",
            "organizations",
            ["organization_id"],
            ["organization_id"],
        )

    with op.batch_alter_table("clients") as batch:
        batch.alter_column("organization_id", nullable=False)
        batch.create_index("ix_clients_organization_id", ["organization_id"])

    with op.batch_alter_table("devices") as batch:
        batch.alter_column("organization_id", nullable=False)
        batch.create_index("ix_devices_organization_id", ["organization_id"])

    with op.batch_alter_table("orders") as batch:
        batch.alter_column("organization_id", nullable=False)
        batch.create_index("ix_orders_organization_id", ["organization_id"])

    with op.batch_alter_table("parts") as batch:
        batch.alter_column("organization_id", nullable=False)
        batch.create_index("ix_parts_organization_id", ["organization_id"])

    with op.batch_alter_table("brands") as batch:
        batch.alter_column("organization_id", nullable=False)
        batch.create_index("ix_brands_organization_id", ["organization_id"])

    with op.batch_alter_table("device_types") as batch:
        batch.alter_column("organization_id", nullable=False)
        batch.create_index("ix_device_types_organization_id", ["organization_id"])

    with op.batch_alter_table("payments") as batch:
        batch.alter_column("organization_id", nullable=False)
        batch.create_index("ix_payments_organization_id", ["organization_id"])


def downgrade() -> None:
    # Удаляем FKs/индексы и колонки organization_id
    with op.batch_alter_table("payments") as batch:
        batch.drop_index("ix_payments_organization_id")
        batch.drop_column("organization_id")

    with op.batch_alter_table("device_types") as batch:
        batch.drop_index("ix_device_types_organization_id")
        batch.drop_column("organization_id")

    with op.batch_alter_table("brands") as batch:
        batch.drop_index("ix_brands_organization_id")
        batch.drop_column("organization_id")

    with op.batch_alter_table("parts") as batch:
        batch.drop_index("ix_parts_organization_id")
        batch.drop_column("organization_id")

    with op.batch_alter_table("orders") as batch:
        batch.drop_index("ix_orders_organization_id")
        batch.drop_column("organization_id")

    with op.batch_alter_table("devices") as batch:
        batch.drop_index("ix_devices_organization_id")
        batch.drop_column("organization_id")

    with op.batch_alter_table("clients") as batch:
        batch.drop_index("ix_clients_organization_id")
        batch.drop_column("organization_id")

    with op.batch_alter_table("employees") as batch:
        batch.drop_constraint("fk_employees_organization_id_organizations", type_="foreignkey")
        batch.drop_index("ix_employees_organization_id")
        batch.drop_column("organization_id")

    # Вернём organizations к одиночной записи
    with op.batch_alter_table("organizations") as batch:
        batch.add_column(sa.Column("singleton_key", sa.BigInteger(), nullable=False, server_default="1"))
        batch.create_index("uq_organizations_singleton_key", ["singleton_key"], unique=True)
        batch.drop_column("owner_user_uuid")

