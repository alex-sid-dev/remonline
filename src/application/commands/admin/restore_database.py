import gzip
import json

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.errors._base import PermissionDeniedError
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("restore_database").bind(service="admin")


class RestoreDatabaseCommandHandler:
    """
    Restore data only for the current supervisor's organization from a JSON backup.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _exec(self, sql: str, params: dict | None = None) -> int:
        result = await self._session.execute(text(sql), params or {})
        return result.rowcount or 0

    async def _bulk_insert(self, table: str, rows: list[dict]) -> int:
        if not rows:
            return 0

        columns = list(rows[0].keys())
        cols_sql = ", ".join(columns)
        values_sql = ", ".join(f":{c}" for c in columns)

        stmt = text(f"INSERT INTO {table} ({cols_sql}) VALUES ({values_sql})")
        result = await self._session.execute(stmt, rows)
        return result.rowcount or 0

    async def run(self, archive: bytes, current_employee: Employee) -> None:
        if current_employee.position != EmployeePosition.SUPERVISOR:
            raise PermissionDeniedError(
                message="Только супервизор может восстанавливать базу данных."
            )

        try:
            raw = gzip.decompress(archive)
        except gzip.BadGzipFile:
            raw = archive

        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            logger.error("Invalid backup format (expected JSON)", error=str(exc))
            raise RuntimeError("Неверный формат архива резервной копии (ожидался JSON).") from exc

        org_id = int(current_employee.organization_id)
        backup_org_id = int(payload.get("organization_id", -1))

        if backup_org_id != org_id:
            raise PermissionDeniedError(
                message="Нельзя восстановить данные другой организации из этого архива."
            )

        tables: dict = payload.get("tables") or {}

        logger.warning(
            "Restoring organization from backup",
            organization_id=org_id,
            size=len(raw),
        )

        params = {"org_id": org_id}

        async with self._session.begin():
            # 1. Очистка данных организации (в порядке зависимостей).
            await self._exec(
                """
                DELETE FROM order_comments
                WHERE order_id IN (
                    SELECT order_id FROM orders WHERE organization_id = :org_id
                )
                """,
                params,
            )

            await self._exec(
                """
                DELETE FROM order_parts
                WHERE order_id IN (
                    SELECT order_id FROM orders WHERE organization_id = :org_id
                )
                """,
                params,
            )

            await self._exec(
                """
                DELETE FROM works
                WHERE order_id IN (
                    SELECT order_id FROM orders WHERE organization_id = :org_id
                )
                """,
                params,
            )

            await self._exec(
                "DELETE FROM payments WHERE organization_id = :org_id",
                params,
            )

            await self._exec(
                "DELETE FROM orders WHERE organization_id = :org_id",
                params,
            )

            await self._exec(
                "DELETE FROM devices WHERE organization_id = :org_id",
                params,
            )

            await self._exec(
                "DELETE FROM parts WHERE organization_id = :org_id",
                params,
            )

            await self._exec(
                "DELETE FROM brands WHERE organization_id = :org_id",
                params,
            )

            await self._exec(
                "DELETE FROM device_types WHERE organization_id = :org_id",
                params,
            )

            await self._exec(
                "DELETE FROM clients WHERE organization_id = :org_id",
                params,
            )

            # Users & employees, привязанные к этой организации.
            await self._exec(
                """
                DELETE FROM users
                WHERE user_id IN (
                    SELECT user_id FROM employees WHERE organization_id = :org_id
                )
                """,
                params,
            )

            await self._exec(
                "DELETE FROM employees WHERE organization_id = :org_id",
                params,
            )

            await self._exec(
                "DELETE FROM organizations WHERE organization_id = :org_id",
                params,
            )

            # 2. Вставка данных из бэкапа (в порядке зависимостей).
            await self._bulk_insert("organizations", tables.get("organizations", []))
            await self._bulk_insert("users", tables.get("users", []))
            await self._bulk_insert("employees", tables.get("employees", []))
            await self._bulk_insert("clients", tables.get("clients", []))
            await self._bulk_insert("device_types", tables.get("device_types", []))
            await self._bulk_insert("brands", tables.get("brands", []))
            await self._bulk_insert("parts", tables.get("parts", []))
            await self._bulk_insert("devices", tables.get("devices", []))
            await self._bulk_insert("orders", tables.get("orders", []))
            await self._bulk_insert("payments", tables.get("payments", []))
            await self._bulk_insert("works", tables.get("works", []))
            await self._bulk_insert("order_comments", tables.get("order_comments", []))
            await self._bulk_insert("order_parts", tables.get("order_parts", []))

        logger.info("Organization data restored successfully", organization_id=org_id)
