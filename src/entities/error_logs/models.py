from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ErrorLog:
    level: str
    error_type: str
    message: str
    status_code: int
    path: str
    method: str
    traceback: str | None = None
    id: int | None = field(default=None)
    created_at: datetime | None = field(default=None)
