from typing import Protocol

from src.entities.error_logs.models import ErrorLog


class ErrorLogWriter(Protocol):
    async def write(self, error_log: ErrorLog) -> None: ...
