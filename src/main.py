from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.application.ports.error_log_writer import ErrorLogWriter
from src.config.db_tables import map_tables
from src.config.exc_handlers import ERROR_LOG_WRITER_STATE_KEY, setup_exc_handlers
from src.config.ioc.di import get_providers
from src.config.logging import setup_logging
from src.config.rate_limit import create_limiter
from src.config.settings import Settings
from src.make_supervisor import make_supervisor
from src.presentation.api.rest.v1.routers import api_v1_router

settings = Settings()
setup_logging(level=settings.app.log_level, debug=settings.app.debug)
logger = structlog.get_logger(__name__)

container: AsyncContainer = make_async_container(*get_providers(settings))
limiter = create_limiter(settings.app.rate_limit_default)


@asynccontextmanager
async def lifespan(fast_app: FastAPI) -> AsyncIterator[None]:
    """
    Asynchronous context manager for managing the lifespan of the FastAPI application.
    """
    setattr(
        fast_app.state,
        ERROR_LOG_WRITER_STATE_KEY,
        await container.get(ErrorLogWriter),
    )
    await make_supervisor(container)
    logger.info("Starting application...")
    yield
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    Registers middleware (CORS, rate limit), exception handlers, Dishka DI
    and the v1 REST router under /api.
    """
    map_tables()

    fast_app = FastAPI(
        title=settings.app.title,
        version=settings.app.version,
        description="RemOnline: REST API сервисного центра (заказы, сотрудники, запчасти, статистика)",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        debug=settings.app.debug,
    )

    fast_app.add_middleware(  # type: ignore[call-arg]
        CORSMiddleware,  # type: ignore[arg-type]
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fast_app.state.limiter = limiter
    fast_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    setup_dishka(container, fast_app)
    setup_exc_handlers(fast_app)
    fast_app.include_router(api_v1_router, prefix="/api")

    return fast_app


app = create_app()
