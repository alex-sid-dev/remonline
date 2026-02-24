from abc import ABC, abstractmethod

from src.application.models.auth_token import AuthToken
from src.application.models.user_info import UserInfo


class AdminManager(ABC):
    """Boundary for administrative operations in Keycloak (user lifecycle)."""

    @abstractmethod
    async def register_user(self, email: str, password: str) -> str: ...

    @abstractmethod
    async def delete_user(self, user_uuid: str) -> bytes: ...

    @abstractmethod
    async def update_password(self, user_uuid: str, new_password: str) -> None: ...

    @abstractmethod
    async def update_email(self, user_uuid: str, email: str) -> None: ...

    @abstractmethod
    async def set_user_email_verified(self, user_uuid: str) -> None: ...


class OpenIDManager(ABC):
    """Boundary for OpenID Connect auth flows handled by Keycloak."""

    @abstractmethod
    async def login(self, email: str, password: str) -> AuthToken: ...

    @abstractmethod
    async def get_new_access_token(self, refresh_token: str) -> AuthToken: ...

    @abstractmethod
    async def logout(self, refresh_token: str) -> dict: ...

    @abstractmethod
    async def get_user_info(self, access_token: str) -> UserInfo: ...

    @abstractmethod
    async def verify_token(self, access_token: str) -> dict: ...
