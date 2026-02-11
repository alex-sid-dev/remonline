from abc import ABC, abstractmethod

from src.entities.base_entity import BaseEntity, OIDType, OUUIDType


class Transaction(ABC):
    """Abstraction over unit-of-work transaction."""

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...


class EntitySaver(ABC):
    """Abstraction for persisting and deleting domain entities."""

    @abstractmethod
    def add_one(self, entity: BaseEntity[OIDType, OUUIDType]) -> None: ...

    @abstractmethod
    async def delete(self, entity: BaseEntity[OIDType, OUUIDType]) -> None: ...
