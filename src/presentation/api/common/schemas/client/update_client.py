from pydantic import BaseModel, Field


class UpdateClientSchema(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, min_length=10, max_length=20)
    email: str | None = None
    telegram_nick: str | None = None
    comment: str | None = None
    address: str | None = Field(None, max_length=1024)
    is_active: bool | None = None
