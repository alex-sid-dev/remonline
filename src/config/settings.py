from typing import List, Tuple, Type
from pydantic import Field, BaseModel, AliasChoices
from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict, 
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
    EnvSettingsSource,
    DotEnvSettingsSource
)

from src.config.database import DatabaseSettings
from src.config.keycloak import KeyCloakSettings

class AppSettings(BaseModel):
    """General application settings."""
    title: str = "Remonline API"
    version: str = "1.0.0"
    debug: bool = False
    uvicorn_host: str = Field("0.0.0.0", validation_alias=AliasChoices("uvicorn_host", "UVICORN_HOST"))
    uvicorn_port: int = Field(8000, validation_alias=AliasChoices("uvicorn_port", "UVICORN_PORT"))
    cors_origins: List[str] = ["http://localhost", "http://localhost:8000", "http://localhost:5173", "http://127.0.0.1:5173"]

class Settings(BaseSettings):
    """
    Main application settings that combines all configuration objects.
    """
    model_config = SettingsConfigDict(
        toml_file="settings.toml",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
        env_prefix=""
    )

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    keycloak: KeyCloakSettings = Field(default_factory=KeyCloakSettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            env_settings,
            dotenv_settings,
            init_settings,
            TomlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )

    @property
    def database_url(self) -> str:
        return self.database.database_url
