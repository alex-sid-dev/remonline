import asyncio
import gzip
from datetime import datetime

import structlog

from src.application.errors._base import PermissionDeniedError
from src.config.database import DatabaseSettings
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

logger = structlog.get_logger("backup_database").bind(service="admin")


class BackupDatabaseCommandHandler:
    def __init__(self, db_settings: DatabaseSettings) -> None:
        self._db = db_settings

    async def run(self, current_employee: Employee) -> tuple[bytes, str]:
        if current_employee.position != EmployeePosition.SUPERVISOR:
            raise PermissionDeniedError(
                message="Только супервизор может создавать резервные копии."
            )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"remonline_backup_{timestamp}.sql.gz"

        dsn = (
            f"postgresql://{self._db.postgres_user}:{self._db.postgres_password}"
            f"@{self._db.postgres_host}:{self._db.postgres_port}/{self._db.postgres_db}"
        )

        process = await asyncio.create_subprocess_exec(
            "pg_dump", "--no-owner", "--no-acl", dsn,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            err_msg = stderr.decode(errors="replace")
            logger.error("pg_dump failed", returncode=process.returncode, stderr=err_msg)
            raise RuntimeError(f"pg_dump failed: {err_msg}")

        compressed = gzip.compress(stdout)

        logger.info(
            "Database backup created",
            filename=filename,
            raw_size=len(stdout),
            compressed_size=len(compressed),
        )
        return compressed, filename
