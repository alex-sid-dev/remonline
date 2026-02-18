from dataclasses import dataclass
from typing import Optional

@dataclass(eq=False)
class ApplicationError(Exception):
    status_code: int = 500
    message: str = "Application error occurred"
    error_code: Optional[str] = None

    def __post_init__(self):
        super().__init__(self.message)

@dataclass(eq=False)
class DomainError(ApplicationError):
    status_code: int = 400
    message: str = "Domain error occurred"

@dataclass(eq=False)
class FieldError(DomainError):
    status_code: int = 422
    message: str = "Invalid field data"

@dataclass(eq=False)
class EntityNotFoundError(ApplicationError):
    status_code: int = 404
    message: str = "Entity not found"

@dataclass(eq=False)
class ConflictError(ApplicationError):
    status_code: int = 409
    message: str = "Conflict occurred"

@dataclass(eq=False)
class AuthenticationError(ApplicationError):
    status_code: int = 401
    message: str = "Authentication failed"


@dataclass(eq=False)
class PermissionDeniedError(ApplicationError):
    status_code: int = 403
    message: str = "You are not allowed to perform this action"

@dataclass(eq=False)
class KeycloakError(ApplicationError):
    status_code: int = 503
    message: str = "External auth service unavailable"

@dataclass(eq=False)
class S3Error(ApplicationError):
    status_code: int = 500
    message: str = "S3 storage error"

@dataclass(eq=False)
class FileError(ApplicationError):
    status_code: int = 500
    message: str = "File system error"

@dataclass(eq=False)
class VaultError(ApplicationError):
    status_code: int = 500
    message: str = "Secret storage error"

@dataclass(eq=False)
class ProductCardError(ApplicationError):
    status_code: int = 422
    message: str = "Product card validation error"

@dataclass(eq=False)
class PhiError(ApplicationError):
    status_code: int = 500
    message: str = "AI service error (Phi)"

@dataclass(eq=False)
class QwenError(ApplicationError):
    status_code: int = 500
    message: str = "AI service error (Qwen)"
