from typing import cast

from src.entities.users.models import User, UserID


class UserService:
    """Domain service for higher-level user creation logic."""

    @staticmethod
    def create_user(
        user_uuid: str,
        email: str,
    ) -> User:
        """Create a new user aggregate with DB-assigned id placeholder."""
        return User(
            id=cast(UserID, cast(object, None)),
            uuid=user_uuid,
            email=email,
            is_active=True,
        )
