from dataclasses import dataclass
from typing import Protocol


@dataclass
class OrderStatRow:
    """Per-closed-order aggregated data returned by the adapter."""

    order_id: int
    creator_id: int | None
    assigned_employee_id: int | None
    works_revenue: float
    parts_revenue: float  # выручка от запчастей (цена в заказе * qty)
    parts_cost: float  # затраты на запчасти (цена из справочника запчастей * qty)


class StatisticsReader(Protocol):
    async def get_closed_orders_stats(self) -> list[OrderStatRow]:
        """Return per-order revenue/expenses for all closed active orders."""
        ...
