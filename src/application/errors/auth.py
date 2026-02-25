from dataclasses import dataclass

from src.application.errors._base import (
    AuthenticationError,
    ConflictError,
    DomainError,
    EntityNotFoundError,
    PermissionDeniedError,
)


@dataclass(eq=False)
class InvalidPasswordError(AuthenticationError):
    message: str = "Invalid password"


@dataclass(eq=False)
class HashesDoNotMatchError(AuthenticationError):
    message: str = "Calculated hash does not match the received hash"


@dataclass(eq=False)
class TokenInvalidError(AuthenticationError):
    message: str = "Invalid or expired access token"


@dataclass(eq=False)
class AuthDateExpiredError(AuthenticationError):
    message: str = "Auth date expired"


@dataclass(eq=False)
class InvalidRefreshTokenError(AuthenticationError):
    message: str = "Invalid refresh token"


@dataclass(eq=False)
class EmailNotFoundError(EntityNotFoundError):
    message: str = "Email is not found"


@dataclass(eq=False)
class UserNotFoundError(EntityNotFoundError):
    message: str = "User is not found"


@dataclass(eq=False)
class EmailAlreadyExistsError(ConflictError):
    message: str = "Email already exists"


@dataclass(eq=False)
class InvalidAccessTokenError(AuthenticationError):
    message: str = "Invalid access token"


@dataclass(eq=False)
class InvalidAccessTokenErrorPerm(PermissionDeniedError):
    message: str = "You are not allowed to perform this action"


@dataclass(eq=False)
class NotFoundTokenError(AuthenticationError):
    message: str = "Token not found"


@dataclass(eq=False)
class LifeTimeLiveTokenError(AuthenticationError):
    message: str = "Token expired! Next email in your mailbox"


@dataclass(eq=False)
class InvalidTimeZoneError(DomainError):
    message: str = "Invalid time zone"
