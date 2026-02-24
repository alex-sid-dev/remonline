from pydantic import BaseModel, Field


class UpdateOrderPartSchema(BaseModel):
    qty: int | None = Field(None, description="Quantity of parts")
    price: float | None = Field(None, description="Price per unit")
