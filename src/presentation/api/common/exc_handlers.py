from typing import TYPE_CHECKING
import structlog
from starlette.responses import JSONResponse

if TYPE_CHECKING:
    from starlette.requests import Request
    from src.application.errors._base import ApplicationError

logger = structlog.get_logger(__name__)

async def application_error_handler(_: "Request", exc: "ApplicationError") -> JSONResponse:
    """Глобальный обработчик для всех ошибок приложения (наследников ApplicationError)"""
    
    error_data = {
        "detail": exc.message,
    }
    
    if exc.error_code:
        error_data["error_code"] = exc.error_code
        
    # Логируем ошибки 500 как ошибки, остальные как ворнинги
    if exc.status_code >= 500:
        logger.error(
            "Application error occurred",
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            exc_info=True
        )
    else:
        logger.warning(
            "Application exception",
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code
        )

    return JSONResponse(
        content=error_data,
        status_code=exc.status_code
    )

async def validate(_: "Request", exc: Exception, status: int) -> JSONResponse:
    """Старый обработчик для обратной совместимости, если где-то еще используется"""
    message = getattr(exc, "message", str(exc))
    return JSONResponse(content={"detail": message}, status_code=status)
