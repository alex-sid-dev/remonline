from src.application.errors.part import PartStockNotEnoughError
from src.entities.parts.models import Part


def decrease_stock(part: Part, qty: int) -> None:
    if part.stock_qty is None:
        return
    if qty <= 0:
        raise PartStockNotEnoughError(
            message="Количество запчасти в заказе должно быть положительным"
        )
    current_stock = part.stock_qty or 0
    if current_stock < qty:
        raise PartStockNotEnoughError(
            message=f"Недостаточно запчастей на складе. Доступно: {current_stock}, запрошено: {qty}",
        )
    part.stock_qty = current_stock - qty


def increase_stock(part: Part, qty: int) -> None:
    if part.stock_qty is None:
        return
    part.stock_qty = (part.stock_qty or 0) + qty


def adjust_stock_delta(part: Part, old_qty: int, new_qty: int) -> None:
    if part.stock_qty is None:
        return
    if new_qty <= 0:
        raise PartStockNotEnoughError(
            message="Количество запчасти в заказе должно быть положительным"
        )
    delta = new_qty - old_qty
    current_stock = part.stock_qty or 0
    if delta > 0 and current_stock < delta:
        raise PartStockNotEnoughError(
            message=f"Недостаточно запчастей на складе. Доступно: {current_stock}, требуется дополнительно: {delta}",
        )
    part.stock_qty = current_stock - delta
