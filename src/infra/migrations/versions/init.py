"""create users, employees, clients tables with updated_at trigger

Revision ID: full_postgres_migration
Revises:
Create Date: 2026-02-05 12:45:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import BIGINT, BOOLEAN, TIMESTAMP, UUID

# revision identifiers, used by Alembic.
revision = "full_postgres_migration"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Users table ---
    op.create_table(
        "users",
        sa.Column("user_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column(
            "user_uuid", UUID(as_uuid=True), nullable=False, comment="Keycloak user id (JWT sub)"
        ),
        sa.Column("is_active", BOOLEAN, nullable=False, server_default=sa.text("true")),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_users_user_uuid", "users", ["user_uuid"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --- Employees table ---
    op.create_table(
        "employees",
        sa.Column("employee_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("employee_uuid", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column(
            "user_id",
            BIGINT,
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column(
            "position",
            sa.String(50),
            nullable=False,
            comment="master | manager | admin | supervisor",
        ),
        sa.Column("is_active", BOOLEAN, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
    )

    # --- Clients table ---
    op.create_table(
        "clients",
        sa.Column("client_id", BIGINT, primary_key=True, autoincrement=True),
        sa.Column("client_uuid", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("telegram_nick", sa.String(255), nullable=True),
        sa.Column("comment", sa.String(1024), nullable=True),
        sa.Column("is_active", BOOLEAN, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_clients_phone", "clients", ["phone"])
    op.create_index("ix_clients_email", "clients", ["email"])
    op.create_index("ix_clients_client_uuid", "clients", ["client_uuid"], unique=True)
    op.create_index("ix_employees_employee_uuid", "employees", ["employee_uuid"], unique=True)

    # --- Trigger function to update updated_at ---
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
               language 'plpgsql';
               """)

    # --- Attach trigger to tables ---
    for table in ["users", "employees", "clients"]:
        op.execute(f"""
        CREATE TRIGGER {table}_updated_at_trigger
        BEFORE UPDATE ON {table}
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers
    for table in ["clients", "employees", "users"]:
        op.execute(f"DROP TRIGGER IF EXISTS {table}_updated_at_trigger ON {table};")

    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop tables
    op.drop_index("ix_clients_email", table_name="clients")
    op.drop_index("ix_clients_phone", table_name="clients")
    op.drop_table("clients")

    op.drop_table("employees")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_user_uuid", table_name="users")
    op.drop_table("users")
