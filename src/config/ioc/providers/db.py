from dishka import Provider, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.ioc.providers.db_provider import get_engine, get_session, get_sessionmaker


def db_provider() -> Provider:
    provider = Provider(scope=Scope.REQUEST)
    _ = provider.provide(get_engine, scope=Scope.APP)
    _ = provider.provide(get_sessionmaker, scope=Scope.APP)
    _ = provider.provide(get_session, provides=AsyncSession)
    return provider
