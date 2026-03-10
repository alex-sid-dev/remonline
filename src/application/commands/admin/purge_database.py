import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.errors._base import PermissionDeniedError
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("purge_database").bind(service="admin")


class PurgeDatabaseCommandHandler:
    """
    Remove all business data only for the current supervisor's organization.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def run(self, current_employee: Employee) -> dict[str, int]:
        if current_employee.position != EmployeePosition.SUPERVISOR:
            raise PermissionDeniedError(message="Только супервизор может очищать базу данных.")

        org_id = int(current_employee.organization_id)
        deleted: dict[str, int] = {}

        params = {"org_id": org_id}

        # Удаляем данные только для текущей организации, в порядке зависимостей.
        result = await self._session.execute(
            text(
                """
                DELETE FROM order_comments
                WHERE order_id IN (
                    SELECT order_id FROM orders WHERE organization_id = :org_id
                )
                """
            ),
            params,
        )
        deleted["order_comments"] = result.rowcount or 0

        result = await self._session.execute(
            text(
                """
                DELETE FROM order_parts
                WHERE order_id IN (
                    SELECT order_id FROM orders WHERE organization_id = :org_id
                )
                """
            ),
            params,
        )
        deleted["order_parts"] = result.rowcount or 0

        result = await self._session.execute(
            text(
                """
                DELETE FROM works
                WHERE order_id IN (
                    SELECT order_id FROM orders WHERE organization_id = :org_id
                )
                """
            ),
            params,
        )
        deleted["works"] = result.rowcount or 0

        result = await self._session.execute(
            text("DELETE FROM payments WHERE organization_id = :org_id"),
            params,
        )
        deleted["payments"] = result.rowcount or 0

        result = await self._session.execute(
            text("DELETE FROM orders WHERE organization_id = :org_id"),
            params,
        )
        deleted["orders"] = result.rowcount or 0

        result = await self._session.execute(
            text("DELETE FROM devices WHERE organization_id = :org_id"),
            params,
        )
        deleted["devices"] = result.rowcount or 0

        result = await self._session.execute(
            text("DELETE FROM device_types WHERE organization_id = :org_id"),
            params,
        )
        deleted["device_types"] = result.rowcount or 0

        result = await self._session.execute(
            text("DELETE FROM brands WHERE organization_id = :org_id"),
            params,
        )
        deleted["brands"] = result.rowcount or 0

        result = await self._session.execute(
            text("DELETE FROM parts WHERE organization_id = :org_id"),
            params,
        )
        deleted["parts"] = result.rowcount or 0

        result = await self._session.execute(
            text("DELETE FROM clients WHERE organization_id = :org_id"),
            params,
        )
        deleted["clients"] = result.rowcount or 0

        # employees: оставить только супервизоров организации
        result = await self._session.execute(
            text(
                """
                DELETE FROM employees
                WHERE organization_id = :org_id AND position != 'supervisor'
                """
            ),
            params,
        )
        deleted["employees"] = result.rowcount or 0

        # users: оставить только пользователей-супервизоров этой организации
        result = await self._session.execute(
            text(
                """
                DELETE FROM users
                WHERE user_id IN (
                    SELECT user_id
                    FROM employees
                    WHERE organization_id = :org_id AND position != 'supervisor'
                )
                """
            ),
            params,
        )
        deleted["users"] = result.rowcount or 0

        await self._session.commit()
        logger.info("Database purged for organization", organization_id=org_id, deleted=deleted)
        return deleted
