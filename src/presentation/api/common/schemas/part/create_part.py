from pydantic import BaseModel


class CreatePartSchema(BaseModel):
    name: str
    sku: str | None = None
    price: float | None = None
    stock_qty: int | None = None


class UpdatePartSchema(BaseModel):
    name: str | None = None
    sku: str | None = None
    price: float | None = None
    stock_qty: int | None = None
    is_active: bool | None = None
