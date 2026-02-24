from typing import final

from pydantic import AliasChoices, BaseModel, Field


@final
class DatabaseSettings(BaseModel):
    """
    Database configuration settings.
    """

    postgres_user: str = Field(..., validation_alias=AliasChoices("postgres_user", "POSTGRES_USER"))
    postgres_password: str = Field(
        ..., validation_alias=AliasChoices("postgres_password", "POSTGRES_PASSWORD")
    )
    postgres_host: str = Field(
        "127.0.0.1", validation_alias=AliasChoices("postgres_host", "POSTGRES_HOST")
    )
    postgres_port: int = Field(
        5432, validation_alias=AliasChoices("postgres_port", "POSTGRES_PORT")
    )
    postgres_db: str = Field(
        "remonline", validation_alias=AliasChoices("postgres_db", "POSTGRES_DB")
    )
    postgres_scheme: str = Field(
        "postgresql+psycopg", validation_alias=AliasChoices("postgres_scheme", "POSTGRES_SCHEME")
    )

    # Connection pool and logging configuration
    echo: bool = Field(False, validation_alias=AliasChoices("echo", "DB_ECHO"))
    pool_size: int = Field(15, validation_alias=AliasChoices("pool_size", "DB_POOL_SIZE"))
    max_overflow: int = Field(15, validation_alias=AliasChoices("max_overflow", "DB_MAX_OVERFLOW"))
    pool_timeout: int = Field(5, validation_alias=AliasChoices("pool_timeout", "DB_POOL_TIMEOUT"))

    @property
    def database_url(self) -> str:
        """
        Constructs the PostgreSQL database URL.
        """
        return f"{self.postgres_scheme}://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
