import base64
import json
import traceback as tb_module
import uuid

import structlog
from fastapi import FastAPI
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DatabaseError, IntegrityError, OperationalError
from sqlalchemy.exc import TimeoutError as SATimeoutError
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.application.errors._base import (
    ApplicationError,
    AuthenticationError,
    ConflictError,
    DomainError,
    EntityNotFoundError,
    FieldError,
    FileError,
    KeycloakError,
    PermissionDeniedError,
    PhiError,
    ProductCardError,
    QwenError,
    S3Error,
    VaultError,
)
from src.application.ports.error_log_writer import ErrorLogWriter
from src.entities.error_logs.models import ErrorLog

logger = structlog.get_logger(__name__)

ERROR_LOG_WRITER_STATE_KEY = "error_log_writer"

# ---------------------------------------------------------------------------
# ApplicationError subclass → HTTP status code.
# Looked up via MRO, so insertion order does not matter.
# ---------------------------------------------------------------------------
ERROR_STATUS_MAP: dict[type, int] = {
    EntityNotFoundError: 404,
    AuthenticationError: 401,
    PermissionDeniedError: 403,
    ConflictError: 409,
    FieldError: 422,
    ProductCardError: 422,
    DomainError: 400,
    KeycloakError: 503,
    S3Error: 500,
    FileError: 500,
    VaultError: 500,
    PhiError: 500,
    QwenError: 500,
}

# ---------------------------------------------------------------------------
# SQLAlchemy exception → (status_code, user_message, persist_to_db).
# ---------------------------------------------------------------------------
DB_ERROR_MAP: dict[type[Exception], tuple[int, str, bool]] = {
    IntegrityError: (409, "Конфликт данных: запись с такими значениями уже существует", True),
    OperationalError: (503, "Сервис временно недоступен. Попробуйте позже", False),
    SATimeoutError: (504, "Превышено время ожидания. Попробуйте позже", False),
    DatabaseError: (500, "Внутренняя ошибка базы данных", True),
}


def resolve_status_code(exc: ApplicationError) -> int:
    """Walk the exception's MRO and return the first mapped status code."""
    for cls in type(exc).__mro__:
        if cls in ERROR_STATUS_MAP:
            return ERROR_STATUS_MAP[cls]
    return 500


def format_traceback(exc: Exception) -> str:
    return "".join(tb_module.format_exception(type(exc), exc, exc.__traceback__))


def _extract_user_hint(request: Request) -> str | None:
    """Best-effort JWT *sub* extraction for logging (no signature verification)."""
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        payload_b64 = auth[7:].split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload_b64))
        return data.get("sub") or data.get("email")
    except Exception:  # noqa: BLE001
        return None


def _get_writer(request: Request) -> ErrorLogWriter | None:
    """Retrieve the ``ErrorLogWriter`` stored on ``app.state`` during lifespan."""
    return getattr(request.app.state, ERROR_LOG_WRITER_STATE_KEY, None)


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------
def setup_exc_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application."""

    # -- helpers -----------------------------------------------------------

    async def _persist(
        request: Request,
        status_code: int,
        error_type: str,
        message: str,
        level: str,
        tb: str | None = None,
    ) -> None:
        writer = _get_writer(request)
        if writer is None:
            logger.error("ErrorLogWriter not available on app.state, skipping DB log")
            return
        try:
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
        except Exception:  # noqa: BLE001
            logger.error("Failed to persist error log to DB", exc_info=True)

    async def _handle(
        request: Request,
        status_code: int,
        detail: str,
        error_type: str,
        exc: Exception,
        *,
        persist: bool = True,
        error_code: str | None = None,
    ) -> JSONResponse:
        request_id = uuid.uuid4().hex[:12]
        level = "error" if status_code >= 500 else "warning"

        bound = logger.bind(
            request_id=request_id,
            status_code=status_code,
            error_type=error_type,
            path=str(request.url),
            method=request.method,
            user_hint=_extract_user_hint(request),
        )
        if status_code >= 500:
            bound.error("Server error", exc_info=True)
        else:
            bound.warning("Client error")

        if persist:
            await _persist(
                request,
                status_code,
                error_type,
                detail,
                level,
                tb=format_traceback(exc) if status_code >= 500 else None,
            )

        body: dict[str, str] = {"detail": detail, "request_id": request_id}
        if error_code:
            body["error_code"] = error_code
        return JSONResponse(content=body, status_code=status_code)

    # -- Application errors ------------------------------------------------

    async def application_error_handler(
        request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        return await _handle(
            request,
            resolve_status_code(exc),
            exc.message,
            type(exc).__name__,
            exc,
            error_code=exc.error_code,
        )

    # -- Database errors (generated from mapping) --------------------------

    for exc_type, (code, msg, should_persist) in DB_ERROR_MAP.items():

        async def _db_handler(
            request: Request,
            exc: Exception,
            *,
            _code: int = code,
            _msg: str = msg,
            _persist: bool = should_persist,
        ) -> JSONResponse:
            return await _handle(
                request,
                _code,
                _msg,
                type(exc).__name__,
                exc,
                persist=_persist,
            )

        app.add_exception_handler(exc_type, _db_handler)

    # -- Catch-all for truly unexpected errors -----------------------------

    async def unhandled_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return await _handle(
            request,
            500,
            "Внутренняя ошибка сервера",
            type(exc).__name__,
            exc,
        )

    # При ошибке валидации на логине возвращаем 401 "Неверный пароль", чтобы не раскрывать причину.
    async def login_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        if request.method == "POST" and "auth/login" in request.url.path:
            return JSONResponse(
                status_code=401,
                content={"detail": "Неверный пароль"},
            )
        return await request_validation_exception_handler(request, exc)

    app.add_exception_handler(RequestValidationError, login_validation_handler)
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
