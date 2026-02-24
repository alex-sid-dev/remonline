from dataclasses import dataclass
from typing import Final

import structlog

from src.application.keycloak.auth_managers import OpenIDManager

logger = structlog.get_logger("logout").bind(service="auth")


@dataclass(frozen=True, slots=True)
class LogoutCommand:
    """Command containing refresh token that should be invalidated."""

    refresh_token: str


class LogoutCommandHandler:
    """Use case: invalidate refresh token in Keycloak."""

    def __init__(
        self,
        open_id_manager: OpenIDManager,
    ) -> None:
        self._open_id_manager: Final = open_id_manager

    async def run(self, data: LogoutCommand) -> None:
        logger.info("Logout attempt started", refresh_token=data.refresh_token[:8] + "...")

        try:
            await self._open_id_manager.logout(refresh_token=data.refresh_token)
            logger.info("Logout successful", refresh_token=data.refresh_token[:8] + "...")
        except Exception as e:
            logger.error(
                "Logout failed", refresh_token=data.refresh_token[:8] + "...", error=str(e)
            )
            raise
