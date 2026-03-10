"""Make employee phone unique per organization.

Revision ID: employees_unique_phone_per_org
Revises: multitenant_organizations
Create Date: 2026-03-10
"""

import sqlalchemy as sa
from alembic import op

revision = "employees_unique_phone_per_org"
down_revision = "multitenant_organizations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Найти дубликаты (organization_id, phone), где записей > 1.
    duplicates = conn.execute(
        sa.text(
            """
            SELECT organization_id, phone
            FROM employees
            WHERE phone IS NOT NULL
            GROUP BY organization_id, phone
            HAVING COUNT(*) > 1
            """
        )
    ).fetchall()

    # 2. Для каждой пары оставить телефон только у сотрудника с MIN(employee_id),
    #    а у остальных обнулить phone, чтобы не мешали уникальному индексу.
    for org_id, phone in duplicates:
        # id, который оставляем
        keeper_id = conn.execute(
            sa.text(
                """
                SELECT MIN(employee_id)
                FROM employees
                WHERE organization_id = :org_id AND phone = :phone
                """
            ),
            {"org_id": org_id, "phone": phone},
        ).scalar()

        # Обнуляем phone у остальных.
        conn.execute(
            sa.text(
                """
                UPDATE employees
                SET phone = NULL
                WHERE organization_id = :org_id
                  AND phone = :phone
                  AND employee_id <> :keeper_id
                """
            ),
            {"org_id": org_id, "phone": phone, "keeper_id": keeper_id},
        )

    # 3. Теперь можно спокойно добавить уникальный индекс.
    op.create_index(
        "uq_employees_organization_id_phone",
        "employees",
        ["organization_id", "phone"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_employees_organization_id_phone", table_name="employees")
