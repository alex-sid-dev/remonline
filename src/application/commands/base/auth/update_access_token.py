import structlog
from dataclasses import dataclass
from typing import Final

from src.application.keycloak.auth_managers import OpenIDManager

logger = structlog.get_logger("update_access_token").bind(service="auth")


@dataclass(frozen=True, slots=True)
class UpdateAccessTokenResponse:
    """DTO with a new access / refresh token pair returned from refresh use case."""
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int
    token_type: str


@dataclass(frozen=True, slots=True)
class UpdateAccessTokenCommand:
    """Command that carries a refresh token used to obtain a new access token."""
    refresh_token: str


class UpdateAccessTokenCommandHandler:
    """Use case: exchange refresh token for a new access token via Keycloak."""

    def __init__(
            self,
            open_id_manager: OpenIDManager,
    ) -> None:
        self._open_id_manager: Final = open_id_manager

    async def run(
            self,
            data: UpdateAccessTokenCommand,
    ) -> UpdateAccessTokenResponse:
        logger.info("Refresh token attempt started", refresh_token=data.refresh_token[:8] + "...")

        try:
            auth_token = await self._open_id_manager.get_new_access_token(
                refresh_token=data.refresh_token
            )
            logger.info(
                "Refresh token succeeded",
                access_token=auth_token.access_token[:8] + "...",
                refresh_token=auth_token.refresh_token[:8] + "..."
            )
        except Exception as e:
            logger.error(
                "Refresh token failed",
                refresh_token=data.refresh_token[:8] + "...",
                error=str(e)
            )
            raise

        return UpdateAccessTokenResponse(
            access_token=auth_token.access_token,
            refresh_token=auth_token.refresh_token,
            expires_in=auth_token.expires_in,
            refresh_expires_in=auth_token.refresh_expires_in,
            token_type=auth_token.token_type,
        )
