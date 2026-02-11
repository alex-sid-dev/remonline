import structlog
from keycloak import (
    KeycloakAuthenticationError,
    KeycloakOpenID,
    KeycloakPostError,
)

from src.application.errors.auth import InvalidPasswordError, InvalidRefreshTokenError, InvalidAccessTokenError
from src.application.keycloak.auth_managers import OpenIDManager
from src.application.models.auth_token import AuthToken
from src.application.models.user_info import UserInfo
from src.config.settings import Settings


class KeycloakOpenIDManager(OpenIDManager):
    """Keycloak-based implementation of OpenIDManager for auth flows."""

    def __init__(self, settings: Settings) -> None:
        self._logger = structlog.get_logger("keycloak_openid").bind(service="keycloak_openid")
        self._logger.info("Initializing KeycloakOpenIDManager", server=settings.keycloak.keycloak_url)

        self._client = KeycloakOpenID(
            server_url=settings.keycloak.keycloak_url,
            realm_name=settings.keycloak.keycloak_realm,
            client_id=settings.keycloak.keycloak_client_id,
            verify=True,
        )

    async def login(self, email: str, password: str) -> AuthToken:
        self._logger.info("Attempting login", email=email)
        try:
            auth_token = await self._client.a_token(username=email, password=password)
            self._logger.info("Login successful", email=email)
            return AuthToken(
                access_token=auth_token["access_token"],
                refresh_token=auth_token["refresh_token"],
                expires_in=auth_token["expires_in"],
                refresh_expires_in=auth_token["refresh_expires_in"],
                token_type=auth_token["token_type"],
            )
        except KeycloakAuthenticationError:
            self._logger.warning("Invalid login attempt", email=email)
            raise InvalidPasswordError()

    async def get_new_access_token(self, refresh_token: str) -> AuthToken:
        self._logger.info("Refreshing access token")
        try:
            new_auth_token = await self._client.a_refresh_token(refresh_token=refresh_token)
            self._logger.info("Access token refreshed")
            return AuthToken(
                access_token=new_auth_token["access_token"],
                refresh_token=new_auth_token["refresh_token"],
                expires_in=new_auth_token["expires_in"],
                refresh_expires_in=new_auth_token["refresh_expires_in"],
                token_type=new_auth_token["token_type"],
            )
        except (KeycloakAuthenticationError, KeycloakPostError):
            self._logger.warning("Failed to refresh access token")
            raise InvalidRefreshTokenError()

    async def verify_token(self, access_token: str) -> dict:
        self._logger.info("Verifying access token")
        try:
            return self._client.decode_token(access_token)
        except Exception as e:
            self._logger.warning("Invalid access token")
            from src.application.errors.auth import InvalidAccessTokenError
            raise InvalidAccessTokenError() from e

    async def get_user_info(self, access_token: str) -> UserInfo:
        self._logger.info("Getting user info")
        try:
            user_info = await self._client.a_userinfo(access_token)
            self._logger.info("User info retrieved", user_uuid=user_info["sub"])
            return UserInfo(
                user_uuid=user_info["sub"],
                email=user_info["email"],
                preferred_username=user_info["preferred_username"],
                email_verified=user_info["email_verified"],
            )
        except KeycloakAuthenticationError:
            self._logger.warning("Invalid access token when getting user info")
            raise InvalidAccessTokenError()

    async def logout(self, refresh_token: str) -> dict:
        self._logger.info("Logging out user")
        try:
            result = await self._client.a_logout(refresh_token=refresh_token)
            self._logger.info("User logged out")
            return result
        except (KeycloakAuthenticationError, KeycloakPostError):
            self._logger.warning("Failed to logout user")
            raise InvalidRefreshTokenError()
