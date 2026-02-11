class ApplicationError(Exception):
    @property
    def message(self) -> str:
        return "Application error occurred"

class DomainError(Exception):
    @property
    def message(self) -> str:
        return "Domain error occurred"


class FieldError(DomainError):
    pass

class EntityNotFoundError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class AuthenticationError(ApplicationError):
    pass


class KeycloakError(ApplicationError):
    pass


class S3Error(ApplicationError):
    pass


class FileError(ApplicationError):
    pass


class VaultError(ApplicationError):
    pass


class ProductCardError(ApplicationError):
    pass


class PhiError(ApplicationError):
    pass


class QwenError(ApplicationError):
    pass
