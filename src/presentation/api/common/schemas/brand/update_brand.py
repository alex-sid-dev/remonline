from typing import Optional

from pydantic import BaseModel


class UpdateBrandSchema(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
