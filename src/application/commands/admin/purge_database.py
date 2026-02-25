import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.errors._base import PermissionDeniedError
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("purge_database").bind(service="admin")

TABLES_TO_TRUNCATE = [
    "error_logs",
    "order_comments",
    "order_parts",
    "works",
    "payments",
    "orders",
    "devices",
    "device_types",
    "brands",
    "parts",
    "clients",
    "organizations",
]


class PurgeDatabaseCommandHandler:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def run(self, current_employee: Employee) -> dict[str, int]:
        if current_employee.position != EmployeePosition.SUPERVISOR:
            raise PermissionDeniedError(message="Только супервизор может очищать базу данных.")

        deleted: dict[str, int] = {}

        for table in TABLES_TO_TRUNCATE:
            result = await self._session.execute(
                text(f"DELETE FROM {table}")  # noqa: S608
            )
            deleted[table] = result.rowcount

        # employees: keep only the supervisor
        result = await self._session.execute(
            text("DELETE FROM employees WHERE position != 'supervisor'")
        )
        deleted["employees"] = result.rowcount

        # users: keep only the supervisor's user
        result = await self._session.execute(
            text(
                "DELETE FROM users WHERE user_id NOT IN "
                "(SELECT user_id FROM employees WHERE position = 'supervisor')"
            )
        )
        deleted["users"] = result.rowcount

        await self._session.commit()
        logger.info("Database purged", deleted=deleted)
        return deleted
