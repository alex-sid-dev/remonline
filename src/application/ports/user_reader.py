from abc import ABC, abstractmethod
from src.entities.users.models import User, UserID, UserUUID


class UserReader(ABC):
    """Abstract read-only repository for User entities."""

    @abstractmethod
    async def read_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def read_by_uuid(self, user_uuid: UserUUID) -> User | None: ...

    @abstractmethod
    async def read_by_oid(self, user_oid: UserID) -> User | None: ...
