import traceback
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from src.application.errors._base import ApplicationError

from src.application.errors._base import (
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

logger = structlog.get_logger(__name__)

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


def resolve_status_code(exc: "ApplicationError") -> int:
    for error_type, code in ERROR_STATUS_MAP.items():
        if isinstance(exc, error_type):
            return code
    return 500


def format_traceback(exc: Exception) -> str:
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
