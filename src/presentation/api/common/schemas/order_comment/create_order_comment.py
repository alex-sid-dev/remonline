from uuid import UUID

from pydantic import BaseModel, Field


class CreateOrderCommentSchema(BaseModel):
    order_uuid: UUID = Field(..., description="UUID заказа")
    text: str = Field(..., min_length=1, max_length=2048, description="Текст комментария")

