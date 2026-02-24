from uuid import UUID

from pydantic import BaseModel, Field


class CreateOrderPartSchema(BaseModel):
    order_uuid: UUID = Field(..., description="UUID of the order")
    part_uuid: UUID = Field(..., description="UUID of the part")
    qty: int = Field(..., description="Quantity of parts")
    price: float | None = Field(None, description="Price per unit")
