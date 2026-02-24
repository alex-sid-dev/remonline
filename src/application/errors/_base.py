from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationError(Exception):
    message: str = "Application error occurred"
    error_code: str | None = None

    def __post_init__(self):
        super().__init__(self.message)


@dataclass(eq=False)
class DomainError(ApplicationError):
    message: str = "Domain error occurred"


@dataclass(eq=False)
class FieldError(DomainError):
    message: str = "Invalid field data"


@dataclass(eq=False)
class EntityNotFoundError(ApplicationError):
    message: str = "Entity not found"


@dataclass(eq=False)
class ConflictError(ApplicationError):
    message: str = "Conflict occurred"


@dataclass(eq=False)
class AuthenticationError(ApplicationError):
    message: str = "Authentication failed"


@dataclass(eq=False)
class PermissionDeniedError(ApplicationError):
    message: str = "You are not allowed to perform this action"


@dataclass(eq=False)
class KeycloakError(ApplicationError):
    message: str = "External auth service unavailable"


@dataclass(eq=False)
class S3Error(ApplicationError):
    message: str = "S3 storage error"


@dataclass(eq=False)
class FileError(ApplicationError):
    message: str = "File system error"


@dataclass(eq=False)
class VaultError(ApplicationError):
    message: str = "Secret storage error"


@dataclass(eq=False)
class ProductCardError(ApplicationError):
    message: str = "Product card validation error"


@dataclass(eq=False)
class PhiError(ApplicationError):
    message: str = "AI service error (Phi)"


@dataclass(eq=False)
class QwenError(ApplicationError):
    message: str = "AI service error (Qwen)"
