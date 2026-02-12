import uuid
from typing import Optional
from src.entities.order_parts.models import OrderPart
from src.entities.orders.models import OrderID
from src.entities.parts.models import PartID

class OrderPartService:
    def create_order_part(
            self,
            order_id: OrderID,
            part_id: PartID,
            qty: int,
            price: Optional[float] = None
    ) -> OrderPart:
        return OrderPart(
            id=None,
            uuid=uuid.uuid4(),
            order_id=order_id,
            part_id=part_id,
            qty=qty,
            price=price
        )

    def update_order_part(
            self,
            order_part: OrderPart,
            qty: Optional[int] = None,
            price: Optional[float] = None
    ) -> OrderPart:
        if qty is not None:
            order_part.qty = qty
        if price is not None:
            order_part.price = price
        return order_part
