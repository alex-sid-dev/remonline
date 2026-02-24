from dataclasses import dataclass
from typing import Final

import structlog

from src.application.errors.auth import UserNotFoundError
from src.application.keycloak.auth_managers import OpenIDManager
from src.application.ports.user_reader import UserReader

logger = structlog.get_logger("login").bind(service="auth")


@dataclass(frozen=True, slots=True)
class LoginResponse:
    """DTO returned from the login use case."""

    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int
    token_type: str


@dataclass(frozen=True, slots=True)
class LoginCommand:
    """Command with credentials required to authenticate a user."""

    email: str
    password: str


class LoginCommandHandler:
    """Use case: authenticate seller and issue auth tokens via Keycloak."""

    def __init__(
        self,
        user_reader: UserReader,
        open_id_manager: OpenIDManager,
    ) -> None:
        self._user_reader: Final = user_reader
        self._open_id_manager: Final = open_id_manager

    async def run(self, data: LoginCommand) -> LoginResponse:
        logger.info("Login attempt started", email=data.email)

        user = await self._user_reader.read_by_email(email=data.email)
        if user is None:
            logger.warning("Login failed: user not found", email=data.email)
            raise UserNotFoundError()

        try:
            refresh_and_access_token = await self._open_id_manager.login(
                email=user.email,
                password=data.password,
            )
            logger.info("User logged in successfully", email=user.email, user_uuid=user.uuid)
        except Exception as e:
            logger.error("Login failed", email=data.email, error=str(e))
            raise

        return LoginResponse(
            access_token=refresh_and_access_token.access_token,
            refresh_token=refresh_and_access_token.refresh_token,
            expires_in=refresh_and_access_token.expires_in,
            refresh_expires_in=refresh_and_access_token.refresh_expires_in,
            token_type=refresh_and_access_token.token_type,
        )
