import warnings

from pydantic import AliasChoices, BaseModel, Field, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)
from typing_extensions import Self

from src.config.database import DatabaseSettings
from src.config.keycloak import KeyCloakSettings


class AppSettings(BaseModel):
    """General application settings."""

    title: str = "Remonline API"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    rate_limit_default: str = "200/minute"
    uvicorn_host: str = Field(
        "0.0.0.0", validation_alias=AliasChoices("uvicorn_host", "UVICORN_HOST")
    )
    uvicorn_port: int = Field(8000, validation_alias=AliasChoices("uvicorn_port", "UVICORN_PORT"))
    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @model_validator(mode="after")
    def _warn_cors_localhost_in_production(self) -> Self:
        if not self.debug:
            suspects = [o for o in self.cors_origins if "localhost" in o or "127.0.0.1" in o]
            if suspects:
                warnings.warn(
                    f"CORS origins contain localhost entries in non-debug mode: {suspects}. "
                    "Consider removing them for production deployments.",
                    UserWarning,
                    stacklevel=2,
                )
        return self


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
        env_prefix="",
    )

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    keycloak: KeyCloakSettings = Field(default_factory=KeyCloakSettings)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
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
