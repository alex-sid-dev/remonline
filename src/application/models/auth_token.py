from dataclasses import dataclass


@dataclass
class AuthToken:
    access_token: str
    refresh_token: str
    expires_in: int
    refresh_expires_in: int
    token_type: str
