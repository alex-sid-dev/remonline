from typing import Final

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.base_entity import BaseEntity, IDType, UUIDType


class TransactionAlchemy(Transaction):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session
        self._logger = structlog.get_logger("db").bind(service="db")

    async def commit(self) -> None:
        self._logger.info("Committing transaction")
        await self._session.commit()
        self._logger.info("Transaction committed")

    async def flush(self) -> None:
        self._logger.info("Flushing transaction")
        await self._session.flush()
        self._logger.info("Transaction flushed")

    async def rollback(self) -> None:
        self._logger.info("Rolling back transaction")
        await self._session.rollback()
        self._logger.info("Transaction rolled back")


class EntitySaverAlchemy(EntitySaver):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session
        self._logger = structlog.get_logger("db").bind(service="db")

    def add_one(self, entity: BaseEntity[IDType, UUIDType]) -> None:
        self._session.add(entity)
        self._logger.info("Added entity", entity_id=str(entity.id))

    async def delete(self, entity: BaseEntity[IDType, UUIDType]) -> None:
        await self._session.delete(entity)
        self._logger.info("Deleted entity", entity_id=str(entity.id))
