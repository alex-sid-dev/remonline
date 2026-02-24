from uuid import UUID

from pydantic import BaseModel


class UpdateDeviceSchema(BaseModel):
    brand_uuid: UUID | None = None
    model: str | None = None
    serial_number: str | None = None
    description: str | None = None
    is_active: bool | None = None
