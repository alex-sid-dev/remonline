import structlog
from keycloak import (
    KeycloakAdmin,
    KeycloakAuthenticationError,
    KeycloakConnectionError,
    KeycloakGetError,
    KeycloakPostError,
)

from src.application.errors.keycloak import KeyCloakRuntimeError
from src.application.keycloak.auth_managers import AdminManager
from src.config.settings import Settings


class KeycloakAdminManager(AdminManager):
    """Keycloak-based implementation of the administrative user manager."""

    def __init__(self, settings: Settings) -> None:
        self._logger = structlog.get_logger("keycloak").bind(service="keycloak")
        self._logger.info(
            "Initializing KeycloakAdminManager", server=settings.keycloak.keycloak_url
        )

        self._client = KeycloakAdmin(
            server_url=settings.keycloak.keycloak_url,
            username=settings.keycloak.keycloak_username,
            password=settings.keycloak.keycloak_password,
            realm_name=settings.keycloak.keycloak_realm,
            client_id=settings.keycloak.keycloak_client_id,
            verify=True,
        )

    async def register_user(self, email: str, password: str) -> str:
        self._logger.info("Registering user", email=email)
        new_user = {
            "email": email,
            "username": email,
            "enabled": True,
            "emailVerified": False,
            "credentials": [{"value": password, "type": "password"}],
        }
        try:
            user_id = await self._client.a_create_user(payload=new_user)
            self._logger.info("User registered successfully", email=email, user_id=user_id)
            return user_id
        except (
            KeycloakConnectionError,
            KeycloakGetError,
            KeycloakAuthenticationError,
            KeycloakPostError,
        ) as e:
            self._logger.exception("Keycloak error during user registration", email=email)
            raise KeyCloakRuntimeError() from e

    async def delete_user(self, user_uuid: str) -> bytes:
        self._logger.info("Deleting user", user_uuid=user_uuid)
        try:
            result = await self._client.a_delete_user(user_id=user_uuid)
            self._logger.info("User deleted successfully", user_uuid=user_uuid)
            return result
        except (KeycloakConnectionError, KeycloakGetError) as e:
            self._logger.exception("Keycloak error during user deletion", user_uuid=user_uuid)
            raise KeyCloakRuntimeError() from e

    async def update_password(self, user_uuid: str, new_password: str) -> None:
        self._logger.info("Updating user password", user_uuid=user_uuid)
        try:
            await self._client.a_set_user_password(
                user_id=user_uuid, password=new_password, temporary=False
            )
            self._logger.info("User password updated", user_uuid=user_uuid)
        except (KeycloakConnectionError, KeycloakGetError) as e:
            self._logger.exception("Keycloak error during password update", user_uuid=user_uuid)
            raise KeyCloakRuntimeError() from e

    async def set_user_email_verified(self, user_uuid: str) -> None:
        self._logger.info("Setting user email verified", user_uuid=user_uuid)
        try:
            await self._client.a_update_user(user_id=user_uuid, payload={"emailVerified": True})
            self._logger.info("User email verified set", user_uuid=user_uuid)
        except (KeycloakConnectionError, KeycloakGetError) as e:
            self._logger.exception(
                "Keycloak error during updating email verified status", user_uuid=user_uuid
            )
            raise KeyCloakRuntimeError() from e

    async def update_email(self, user_uuid: str, email: str) -> None:
        self._logger.info("Updating user email", user_uuid=user_uuid, new_email=email)
        try:
            user_data = await self._client.a_get_user(user_id=user_uuid)
            user_data["email"] = email
            await self._client.a_update_user(user_id=user_uuid, payload=user_data)
            self._logger.info("User email updated", user_uuid=user_uuid, new_email=email)
        except (KeycloakConnectionError, KeycloakGetError) as e:
            self._logger.exception(
                "Keycloak error during updating email", user_uuid=user_uuid, new_email=email
            )
            raise KeyCloakRuntimeError() from e
