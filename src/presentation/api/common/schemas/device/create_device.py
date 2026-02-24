from uuid import UUID

from pydantic import BaseModel


class CreateDeviceSchema(BaseModel):
    client_uuid: UUID
    type_uuid: UUID
    brand_uuid: UUID
    model: str
    serial_number: str | None = None
    description: str | None = None
