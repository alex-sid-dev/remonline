from pydantic import Field
from pydantic_settings import BaseSettings

from src.config.database import DatabaseSettings
from src.config.keycloak import KeyCloakSettings



class Settings(BaseSettings):
    """
    Main application settings that combines all configuration objects.

    This class serves as a facade that provides access to all configuration
    sections of the application. Each configuration section is responsible
    for a specific domain (database, redis, cors, etc.).
    """

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    keycloak: KeyCloakSettings = Field(default_factory=KeyCloakSettings)

    @property
    def database_url(self):
        return str(self.database.database_url)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
