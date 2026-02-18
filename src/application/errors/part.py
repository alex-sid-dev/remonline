from dataclasses import dataclass

from src.application.errors._base import ConflictError


@dataclass(eq=False)
class PartStockNotEnoughError(ConflictError):
    """
    Ошибка, возникающая при попытке списать со склада больше запчастей, чем доступно.
    """

    message: str = "Недостаточно запчастей на складе"
    error_code: str | None = "part_stock_not_enough"

