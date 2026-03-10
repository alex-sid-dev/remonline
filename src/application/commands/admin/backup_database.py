import gzip
import json
from datetime import datetime

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.errors._base import PermissionDeniedError
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("backup_database").bind(service="admin")


class BackupDatabaseCommandHandler:
    """
    Create a per-organization logical backup in JSON format, compressed with gzip.

    Only data that belongs to the current supervisor's organization is exported.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _fetch_all(self, sql: str, params: dict | None = None) -> list[dict]:
        result = await self._session.execute(text(sql), params or {})
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    async def run(self, current_employee: Employee) -> tuple[bytes, str]:
        if current_employee.position != EmployeePosition.SUPERVISOR:
            raise PermissionDeniedError(
                message="Только супервизор может создавать резервные копии."
            )

        org_id = int(current_employee.organization_id)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Имя файла сохраняем в прежнем формате для совместимости с фронтом.
        filename = f"remonline_backup_{timestamp}.sql.gz"

        logger.info("Starting organization-level backup", organization_id=org_id)

        # Основные сущности организации.
        organizations = await self._fetch_all(
            "SELECT * FROM organizations WHERE organization_id = :org_id",
            {"org_id": org_id},
        )

        employees = await self._fetch_all(
            "SELECT * FROM employees WHERE organization_id = :org_id",
            {"org_id": org_id},
        )

        users = await self._fetch_all(
            """
            SELECT u.*
            FROM users AS u
            JOIN employees AS e ON e.user_id = u.user_id
            WHERE e.organization_id = :org_id
            """,
            {"org_id": org_id},
        )

        clients = await self._fetch_all(
            "SELECT * FROM clients WHERE organization_id = :org_id",
            {"org_id": org_id},
        )

        devices = await self._fetch_all(
            "SELECT * FROM devices WHERE organization_id = :org_id",
            {"org_id": org_id},
        )

        device_types = await self._fetch_all(
            "SELECT * FROM device_types WHERE organization_id = :org_id",
            {"org_id": org_id},
        )

        brands = await self._fetch_all(
            "SELECT * FROM brands WHERE organization_id = :org_id",
            {"org_id": org_id},
        )

        parts = await self._fetch_all(
            "SELECT * FROM parts WHERE organization_id = :org_id",
            {"org_id": org_id},
        )

        orders = await self._fetch_all(
            "SELECT * FROM orders WHERE organization_id = :org_id",
            {"org_id": org_id},
        )

        # Таблицы, завязанные на заказы компании.
        order_comments = await self._fetch_all(
            """
            SELECT oc.*
            FROM order_comments AS oc
            WHERE oc.order_id IN (
                SELECT o.order_id FROM orders AS o WHERE o.organization_id = :org_id
            )
            """,
            {"org_id": org_id},
        )

        order_parts = await self._fetch_all(
            """
            SELECT op.*
            FROM order_parts AS op
            WHERE op.order_id IN (
                SELECT o.order_id FROM orders AS o WHERE o.organization_id = :org_id
            )
            """,
            {"org_id": org_id},
        )

        works = await self._fetch_all(
            """
            SELECT w.*
            FROM works AS w
            WHERE w.order_id IN (
                SELECT o.order_id FROM orders AS o WHERE o.organization_id = :org_id
            )
            """,
            {"org_id": org_id},
        )

        payments = await self._fetch_all(
            "SELECT * FROM payments WHERE organization_id = :org_id",
            {"org_id": org_id},
        )

        payload = {
            "version": 1,
            "organization_id": org_id,
            "tables": {
                "organizations": organizations,
                "users": users,
                "employees": employees,
                "clients": clients,
                "devices": devices,
                "device_types": device_types,
                "brands": brands,
                "parts": parts,
                "orders": orders,
                "order_comments": order_comments,
                "order_parts": order_parts,
                "works": works,
                "payments": payments,
            },
        }

        raw_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        compressed = gzip.compress(raw_bytes)

        logger.info(
            "Organization backup created",
            filename=filename,
            organization_id=org_id,
            raw_size=len(raw_bytes),
            compressed_size=len(compressed),
        )
        return compressed, filename
