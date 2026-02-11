import uuid
from dataclasses import dataclass


@dataclass
class UserInfo:
    user_uuid: uuid.UUID
    email: str
    preferred_username: str
    email_verified: bool
