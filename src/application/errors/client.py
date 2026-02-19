from dataclasses import dataclass

from src.application.errors._base import FieldError


@dataclass(eq=False)
class PhoneError(FieldError):
    message: str = "Not valid phone number. Expected format: +78008008000"
