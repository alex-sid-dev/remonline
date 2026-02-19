from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ErrorLog:
    level: str
    error_type: str
    message: str
    status_code: int
    path: str
    method: str
    traceback: Optional[str] = None
    id: Optional[int] = field(default=None)
    created_at: Optional[datetime] = field(default=None)
