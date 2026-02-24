from uuid import uuid4

from src.entities.parts.models import Part, PartUUID


class PartService:
    def create_part(
        self,
        name: str,
        sku: str | None = None,
        price: float | None = None,
        stock_qty: int | None = None,
    ) -> Part:
        return Part(
            id=None,  # type: ignore
            uuid=PartUUID(uuid4()),
            name=name,
            sku=sku,
            price=price,
            stock_qty=stock_qty,
            is_active=True,
        )

    def update_part(
        self,
        part: Part,
        name: str | None = None,
        sku: str | None = None,
        price: float | None = None,
        stock_qty: int | None = None,
        is_active: bool | None = None,
    ) -> Part:
        if name is not None:
            part.name = name
        if sku is not None:
            part.sku = sku
        if price is not None:
            part.price = price
        if stock_qty is not None:
            part.stock_qty = stock_qty
        if is_active is not None:
            part.is_active = is_active
        return part
