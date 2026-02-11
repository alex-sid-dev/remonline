import structlog

from src.config.settings import Settings

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncIterator

logger = structlog.get_logger("db").bind(service="db")


async def get_engine(settings: Settings) -> AsyncIterator[AsyncEngine]:
    """Create and yield an async SQLAlchemy engine bound to configured database."""
    logger.info(
        "Creating async database engine",
        url=str(settings.database.database_url),
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
    )
    engine = create_async_engine(
        str(settings.database.database_url),
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


async def get_sessionmaker(
        engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the given engine."""
    logger.info("Creating session factory for engine")
    return async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )


async def get_session(
        session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """Yield a single database session from the given factory."""
    logger.info("Starting a new database session")
    async with session_factory() as session:
        yield session
    logger.info("Database session closed")
