from typing import final

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


@final
class DatabaseSettings(BaseSettings):
    """
    Database configuration settings.

    Attributes:
        postgres_user (str): PostgreSQL username.
        postgres_password (str): PostgreSQL password.
        postgres_host (str): PostgreSQL server host.
        postgres_port (int): PostgreSQL server port.
        postgres_db (str): PostgreSQL database name.
    """

    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(..., alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(..., alias="POSTGRES_DB")
    postgres_scheme: str = Field(..., alias="POSTGRES_SCHEME")

    # Connection pool and logging configuration
    echo: bool = Field(False, alias="DB_ECHO")
    pool_size: int = Field(15, alias="DB_POOL_SIZE")
    max_overflow: int = Field(15, alias="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(5, alias="DB_POOL_TIMEOUT")

    @property
    def database_url(self) -> PostgresDsn:
        """
        Constructs the PostgreSQL database URL.

        Returns:
            PostgresDsn: The constructed database URL.
        """
        return PostgresDsn.build(
            scheme=self.postgres_scheme,
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
