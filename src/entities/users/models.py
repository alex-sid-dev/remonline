from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from pydantic import EmailStr

from src.entities.base_entity import BaseEntity

UserID = NewType("UserID", int)
UserUUID = NewType("UserUUID", UUID)


@dataclass
class User(BaseEntity[UserID, UserUUID]):
    email: EmailStr
    is_active: bool

