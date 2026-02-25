from collections.abc import AsyncIterator

import structlog
from dishka import Provider, Scope
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import Settings

logger = structlog.get_logger("db").bind(service="db")


async def _get_engine(settings: Settings) -> AsyncIterator[AsyncEngine]:
    logger.info(
        "Creating async database engine",
        url=settings.database.database_url_safe,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
    )
    engine = create_async_engine(
        settings.database.database_url,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_timeout=settings.database.pool_timeout,
    )
    try:
        yield engine
    finally:
        logger.info("Disposing async database engine")
        await engine.dispose()


async def _get_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def _get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


def db_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    provider.provide(_get_engine, scope=Scope.APP)
    provider.provide(_get_sessionmaker, scope=Scope.APP)
    provider.provide(_get_session, provides=AsyncSession)
    return provider
