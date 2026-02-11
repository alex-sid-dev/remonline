from dataclasses import dataclass

from src.application.errors._base import AuthenticationError, EntityNotFoundError, ConflictError


@dataclass
class InvalidPasswordError(AuthenticationError):

    @property
    def message(self) -> str:
        return "Invalid password"


@dataclass
class HashesDoestNotMatchError(AuthenticationError):

    @property
    def message(self) -> str:
        return "Calculated hash does not match the received hash"


@dataclass
class TokenInvalidError(AuthenticationError):

    @property
    def message(self) -> str:
        return "Invalid or expired access token"


@dataclass
class AuthDateExpiredError(AuthenticationError):

    @property
    def message(self) -> str:
        return "Auth date expired"


@dataclass
class InvalidRefreshTokenError(AuthenticationError):

    @property
    def message(self) -> str:
        return "Invalid refresh token"


@dataclass
class EmailNotFoundError(EntityNotFoundError):

    @property
    def message(self) -> str:
        return "Email is not found"


@dataclass
class UserNotFoundError(EntityNotFoundError):

    @property
    def message(self) -> str:
        return "User is not found"


@dataclass
class EmailAlreadyExistsError(ConflictError):

    @property
    def message(self) -> str:
        return "Email already exists"


@dataclass
class InvalidAccessTokenError(AuthenticationError):

    @property
    def message(self) -> str:
        return "Invalid access token"

@dataclass
class InvalidAccessTokenErrorPerm(AuthenticationError):

    @property
    def message(self) -> str:
        return "You are not allowed to perform this action"


@dataclass
class NotFoundTokenError(AuthenticationError):

    @property
    def message(self) -> str:
        return "Token not found"


@dataclass
class LifeTimeLiveTokenError(AuthenticationError):

    @property
    def message(self) -> str:
        return "Token expired! Next email in your mailbox"


@dataclass
class InvalidTimeZoneError(AuthenticationError):

    @property
    def message(self) -> str:
        return "Invalid time zone"
