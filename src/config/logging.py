import logging
import sys

import structlog


def setup_logging(level: str = "INFO", *, debug: bool = False) -> None:
    """Configure *structlog* and the standard-library root logger.

    In debug mode a human-friendly ``ConsoleRenderer`` is used;
    otherwise output is JSON (suitable for production log aggregators).
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    renderer: structlog.types.Processor = (
        structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )
