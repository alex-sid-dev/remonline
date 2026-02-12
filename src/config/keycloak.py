from typing import final
from pydantic import Field, BaseModel, AliasChoices

@final
class KeyCloakSettings(BaseModel):
    keycloak_url: str = Field(..., validation_alias=AliasChoices("keycloak_url", "KEYCLOAK_URL"))
    keycloak_username: str = Field(..., validation_alias=AliasChoices("keycloak_username", "KEYCLOAK_USERNAME"))
    keycloak_password: str = Field(..., validation_alias=AliasChoices("keycloak_password", "KEYCLOAK_PASSWORD"))
    keycloak_realm: str = Field("master", validation_alias=AliasChoices("keycloak_realm", "KEYCLOAK_REALM"))
    keycloak_client_id: str = Field("admin-cli", validation_alias=AliasChoices("keycloak_client_id", "KEYCLOAK_CLIENT_ID"))
