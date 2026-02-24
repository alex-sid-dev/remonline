from pydantic import BaseModel


class UpdateBrandSchema(BaseModel):
    name: str | None = None
    is_active: bool | None = None
