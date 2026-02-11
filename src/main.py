from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from src.config.db_tables import map_tables
from src.config.exc_handlers import setup_exc_handlers
from src.config.ioc.di import get_providers
from src.config.logging import setup_logging
from src.make_admin import make_admin


from src.presentation.api.rest.v1.routers import api_v1_router

setup_logging()
logger = structlog.get_logger(__name__)

container: AsyncContainer = make_async_container(*get_providers())


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """
    Asynchronous context manager for managing the lifespan of the FastAPI application.

    Args:
        _: The FastAPI application instance.

    Yields:
        None
    """
    await make_admin()
    logger.info("Starting application...")
    yield
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    map_tables()

    fast_app = FastAPI(
        title="Base FastAPI",
        version="1.0.0",
        description="Базовый фастапи",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # setup_exc_handlers(fast_app)

    fast_app.add_middleware(  # type: ignore[call-arg]
        CORSMiddleware,  # type: ignore[arg-type]
        allow_origins=[
            "http://localhost",
            "http://localhost:8000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_dishka(container, fast_app)
    setup_exc_handlers(fast_app)
    fast_app.include_router(api_v1_router, prefix="/api")

    return fast_app


app = create_app()
