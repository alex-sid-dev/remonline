from dataclasses import dataclass

from src.application.errors._base import FieldError


@dataclass(eq=False)
class PhoneError(FieldError):
    status_code: int = 422
    message: str = "Not valid phone number. Expected format: +78008008000"