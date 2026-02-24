from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from src.entities.base_entity import BaseEntity

UserID = NewType("UserID", int)
UserUUID = NewType("UserUUID", UUID)


@dataclass
class User(BaseEntity[UserID, UserUUID]):
    email: str
    is_active: bool
