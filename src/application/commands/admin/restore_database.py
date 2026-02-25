import asyncio
import gzip

import structlog

from src.application.errors._base import PermissionDeniedError
from src.config.database import DatabaseSettings
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("restore_database").bind(service="admin")


class RestoreDatabaseCommandHandler:
    def __init__(self, db_settings: DatabaseSettings) -> None:
        self._db = db_settings

    async def run(self, archive: bytes, current_employee: Employee) -> None:
        if current_employee.position != EmployeePosition.SUPERVISOR:
            raise PermissionDeniedError(
                message="Только супервизор может восстанавливать базу данных."
            )

        try:
            sql_data = gzip.decompress(archive)
        except gzip.BadGzipFile:
            sql_data = archive

        dsn = (
            f"postgresql://{self._db.postgres_user}:{self._db.postgres_password}"
            f"@{self._db.postgres_host}:{self._db.postgres_port}/{self._db.postgres_db}"
        )

        logger.warning("Terminating other DB connections and resetting schema")
        reset_sql = (
            "SELECT pg_terminate_backend(pid) "
            "FROM pg_stat_activity "
            "WHERE datname = current_database() AND pid != pg_backend_pid();\n"
            "DROP SCHEMA public CASCADE;\n"
            "CREATE SCHEMA public;\n"
        )
        reset_process = await asyncio.create_subprocess_exec(
            "psql", dsn, "-c", reset_sql,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, reset_err = await asyncio.wait_for(reset_process.communicate(), timeout=30)
        if reset_process.returncode != 0:
            err_msg = reset_err.decode(errors="replace")
            logger.error("Schema reset failed", stderr=err_msg)
            raise RuntimeError(f"Schema reset failed: {err_msg}")

        logger.info("Restoring database from backup", size=len(sql_data))
        restore_process = await asyncio.create_subprocess_exec(
            "psql", dsn,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, restore_err = await asyncio.wait_for(
            restore_process.communicate(input=sql_data), timeout=120,
        )

        if restore_process.returncode != 0:
            err_msg = restore_err.decode(errors="replace")
            logger.error("psql restore failed", returncode=restore_process.returncode, stderr=err_msg)
            raise RuntimeError(f"Database restore failed: {err_msg}")

        logger.info("Database restored successfully")
