from typing import Protocol

from src.entities.users.models import User, UserID, UserUUID


class UserReader(Protocol):
    """Protocol for read-only repository for User entities."""

    async def read_by_email(self, email: str) -> User | None: ...

    async def read_by_uuid(self, user_uuid: UserUUID) -> User | None: ...

    async def read_by_id(self, user_id: UserID) -> User | None: ...
