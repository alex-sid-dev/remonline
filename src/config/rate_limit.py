from slowapi import Limiter
from slowapi.util import get_remote_address


def create_limiter(default_limit: str = "200/minute") -> Limiter:
    return Limiter(key_func=get_remote_address, default_limits=[default_limit])
