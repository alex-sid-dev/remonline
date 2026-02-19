import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Final

from sqlalchemy.orm import selectinload

from src.entities.users.models import User, UserID, UserUUID
from src.infra.models.users import users_table
from src.application.ports.user_reader import UserReader


class UserReaderAdapter(UserReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final = session
        self._logger = structlog.get_logger("db").bind(service="db", entity="user")

    async def read_by_email(self, email: str) -> User | None:
        self._logger.info("Reading user by email", email=email)
        stmt = select(User).where(users_table.c.email == email)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            self._logger.warning("User not found by email", email=email)
        else:
            self._logger.info("User found by email", user_id=user.id)
        return user

    async def read_by_uuid(self, user_uuid: UserUUID) -> User | None:
        self._logger.info("Reading user by UUID", user_uuid=str(user_uuid))
        stmt = (
            select(User)
            .where(users_table.c.user_uuid == user_uuid)
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            self._logger.warning("User not found by UUID", user_uuid=str(user_uuid))
        else:
            self._logger.info("User found by UUID", user_id=user.id)
        return user

    async def read_by_id(self, user_id: UserID) -> User | None:
        self._logger.info("Reading user by ID", user_id=str(user_id))
        stmt = select(User).where(users_table.c.user_id == user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            self._logger.warning("User not found by ID", user_id=str(user_id))
        else:
            self._logger.info("User found by ID", user_id=user.id)
        return user
