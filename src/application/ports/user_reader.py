from typing import Protocol, Optional
from src.entities.users.models import User, UserID, UserUUID

class UserReader(Protocol):
    """Protocol for read-only repository for User entities."""

    async def read_by_email(self, email: str) -> Optional[User]: ...

    async def read_by_uuid(self, user_uuid: UserUUID) -> Optional[User]: ...

    async def read_by_id(self, user_id: UserID) -> Optional[User]: ...
