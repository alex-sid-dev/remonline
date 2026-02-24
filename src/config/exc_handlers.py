import structlog
from dishka import AsyncContainer
from fastapi import FastAPI
from sqlalchemy.exc import DatabaseError, IntegrityError, OperationalError
from sqlalchemy.exc import TimeoutError as SATimeoutError
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.application.errors._base import ApplicationError
from src.application.ports.error_log_writer import ErrorLogWriter
from src.entities.error_logs.models import ErrorLog
from src.presentation.api.common.exc_handlers import (
    format_traceback,
    resolve_status_code,
)

logger = structlog.get_logger(__name__)


async def _write_error_log(
    container: AsyncContainer,
    request: Request,
    status_code: int,
    error_type: str,
    message: str,
    level: str,
    tb: str | None = None,
) -> None:
    try:
        writer = await container.get(ErrorLogWriter)
        await writer.write(
            ErrorLog(
                level=level,
                error_type=error_type,
                message=message[:4096],
                status_code=status_code,
                path=str(request.url),
                method=request.method,
                traceback=tb,
            )
        )
    except Exception:
        logger.error("Failed to persist error log to DB", exc_info=True)


def setup_exc_handlers(app: FastAPI, container: AsyncContainer) -> None:

    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        status_code = resolve_status_code(exc)

        error_data: dict[str, str] = {"detail": exc.message}
        if exc.error_code:
            error_data["error_code"] = exc.error_code

        level = "error" if status_code >= 500 else "warning"
        if status_code >= 500:
            logger.error(
                "Application error occurred",
                status_code=status_code,
                message=exc.message,
                error_code=exc.error_code,
                exc_info=True,
            )
        else:
            logger.warning(
                "Application exception",
                status_code=status_code,
                message=exc.message,
                error_code=exc.error_code,
            )

        await _write_error_log(
            container,
            request,
            status_code,
            type(exc).__name__,
            exc.message,
            level,
            tb=format_traceback(exc) if status_code >= 500 else None,
        )
        return JSONResponse(content=error_data, status_code=status_code)

    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("Database integrity error", detail=str(exc.orig))
        await _write_error_log(
            container,
            request,
            409,
            "IntegrityError",
            str(exc.orig)[:4096],
            "warning",
        )
        return JSONResponse(
            content={"detail": "Конфликт данных: запись с такими значениями уже существует"},
            status_code=409,
        )

    async def operational_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
        logger.error("Database operational error", exc_info=True)
        # DB is likely down -- don't try to write to it
        return JSONResponse(
            content={"detail": "Сервис временно недоступен. Попробуйте позже"},
            status_code=503,
        )

    async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
        logger.error("Database error", exc_info=True)
        await _write_error_log(
            container,
            request,
            500,
            "DatabaseError",
            str(exc.orig)[:4096],
            "error",
            tb=format_traceback(exc),
        )
        return JSONResponse(
            content={"detail": "Внутренняя ошибка базы данных"},
            status_code=500,
        )

    async def timeout_error_handler(request: Request, exc: SATimeoutError) -> JSONResponse:
        logger.error("Database timeout error", exc_info=True)
        # DB timeout -- don't try to write to it
        return JSONResponse(
            content={"detail": "Превышено время ожидания. Попробуйте позже"},
            status_code=504,
        )

    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(OperationalError, operational_error_handler)
    app.add_exception_handler(SATimeoutError, timeout_error_handler)
    app.add_exception_handler(DatabaseError, database_error_handler)
