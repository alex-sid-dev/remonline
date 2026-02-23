from pydantic import BaseModel


class CreateBrandSchema(BaseModel):
    name: str
