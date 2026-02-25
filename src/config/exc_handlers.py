# Backward-compatible re-export; implementation lives in the presentation layer.
from src.presentation.api.common.exc_handlers import (
    ERROR_LOG_WRITER_STATE_KEY,
    setup_exc_handlers,
)

__all__ = ["ERROR_LOG_WRITER_STATE_KEY", "setup_exc_handlers"]
