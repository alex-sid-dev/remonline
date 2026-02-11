from typing import final
from pydantic_settings import BaseSettings
from pydantic import Field


@final
class KeyCloakSettings(BaseSettings):
    keycloak_url: str = Field(..., alias="KEYCLOAK_URL")
    keycloak_username: str = Field(..., alias="KEYCLOAK_USERNAME")
    keycloak_password: str = Field(..., alias="KEYCLOAK_PASSWORD")
    keycloak_realm: str = Field("master", alias="KEYCLOAK_REALM")
    keycloak_client_id: str = Field("admin-cli", alias="KEYCLOAK_CLIENT_ID")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
