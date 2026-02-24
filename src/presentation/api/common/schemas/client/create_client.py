from pydantic import BaseModel, Field, field_validator
from src.presentation.api.common.validators.phone import validate_phone


class CreateClientSchema(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    email: str | None = None
    telegram_nick: str | None = None
    comment: str | None = None
    address: str | None = Field(None, max_length=1024)

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: str) -> str:
        return validate_phone(v)
