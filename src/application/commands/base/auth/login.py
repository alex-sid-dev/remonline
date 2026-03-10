from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final

import structlog

from src.application.errors.auth import InvalidPasswordError
from src.application.keycloak.auth_managers import OpenIDManager
from src.application.ports.user_reader import UserReader

logger = structlog.get_logger("login").bind(service="auth")

# In-memory tracker for failed login attempts (per email + IP).
_FAILED_LOGIN_ATTEMPTS: dict[str, dict[str, object]] = {}
_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_MINUTES = 10
_WINDOW_MINUTES = 15


def _now_utc() -> datetime:
    return datetime.now(tz=UTC)


def _make_attempt_key(email: str, client_ip: str | None) -> str:
    return f"{email.lower()}|{client_ip or 'unknown'}"


def _is_locked(key: str) -> bool:
    state = _FAILED_LOGIN_ATTEMPTS.get(key)
    if not state:
        return False
    locked_until = state.get("locked_until")
    if isinstance(locked_until, datetime) and locked_until > _now_utc():
        return True
    return False


def _register_failure(key: str, *, email: str, client_ip: str | None) -> None:
    now = _now_utc()
    state = _FAILED_LOGIN_ATTEMPTS.get(key, {})
    first_attempt = state.get("first_attempt")
    if not isinstance(first_attempt, datetime) or now - first_attempt > timedelta(
        minutes=_WINDOW_MINUTES,
    ):
        # Сбрасываем окно, если старое.
        state = {"count": 0, "first_attempt": now, "locked_until": None}

    count = int(state.get("count", 0)) + 1
    locked_until: datetime | None = None
    if count >= _MAX_FAILED_ATTEMPTS:
        locked_until = now + timedelta(minutes=_LOCKOUT_MINUTES)
        logger.warning(
            "Too many failed login attempts, locking further attempts",
            email=email,
            client_ip=client_ip,
            until=str(locked_until),
        )

    state["count"] = count
    state["locked_until"] = locked_until
    state["first_attempt"] = state.get("first_attempt", now)
    _FAILED_LOGIN_ATTEMPTS[key] = state


def _reset_failures(key: str) -> None:
    _FAILED_LOGIN_ATTEMPTS.pop(key, None)


@dataclass(frozen=True, slots=True)
class LoginResponse:
    """DTO returned from the login use case."""

    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int
    token_type: str


@dataclass(frozen=True, slots=True)
class LoginCommand:
    """Command with credentials required to authenticate a user."""

    email: str
    password: str
    client_ip: str | None = None


class LoginCommandHandler:
    """Use case: authenticate seller and issue auth tokens via Keycloak."""

    def __init__(
        self,
        user_reader: UserReader,
        open_id_manager: OpenIDManager,
    ) -> None:
        self._user_reader: Final = user_reader
        self._open_id_manager: Final = open_id_manager

    async def run(self, data: LoginCommand) -> LoginResponse:
        key = _make_attempt_key(data.email, data.client_ip)

        if _is_locked(key):
            logger.warning(
                "Login attempt blocked due to lockout",
                email=data.email,
                client_ip=data.client_ip,
            )
            # Специально не раскрываем причину, возвращаем как "Неверный пароль".
            raise InvalidPasswordError()

        logger.info("Login attempt started", email=data.email, client_ip=data.client_ip)

        user = await self._user_reader.read_by_email(email=data.email)
        if user is None:
            logger.warning("Login failed: user not found", email=data.email)
            _register_failure(key, email=data.email, client_ip=data.client_ip)
            raise InvalidPasswordError()

        try:
            refresh_and_access_token = await self._open_id_manager.login(
                email=user.email,
                password=data.password,
            )
            logger.info(
                "User logged in successfully",
                email=user.email,
                user_uuid=user.uuid,
                client_ip=data.client_ip,
            )
            _reset_failures(key)
        except Exception as e:  # noqa: BLE001
            logger.error("Login failed", email=data.email, client_ip=data.client_ip, error=str(e))
            _register_failure(key, email=data.email, client_ip=data.client_ip)
            raise

        return LoginResponse(
            access_token=refresh_and_access_token.access_token,
            refresh_token=refresh_and_access_token.refresh_token,
            expires_in=refresh_and_access_token.expires_in,
            refresh_expires_in=refresh_and_access_token.refresh_expires_in,
            token_type=refresh_and_access_token.token_type,
        )
