import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.entities.error_logs.models import ErrorLog

logger = structlog.get_logger(__name__)


class ErrorLogWriterAdapter:
    """Writes error logs to the DB using an independent session.

    Uses its own short-lived session so that logging does not depend on
    the request's transactional session (which may have already failed).
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def write(self, error_log: ErrorLog) -> None:
        try:
            async with self._session_factory() as session:
                session.add(error_log)
                await session.commit()
        except Exception:
            logger.error(
                "Failed to write error log to DB, falling back to structlog only",
                error_type=error_log.error_type,
                message=error_log.message,
                exc_info=True,
            )
