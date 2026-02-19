from dataclasses import dataclass
from typing import List, Protocol


@dataclass
class OrderStatRow:
    """Per-closed-order aggregated data returned by the adapter."""
    order_id: int
    creator_id: int | None
    assigned_employee_id: int | None
    works_revenue: float
    parts_expenses: float


class StatisticsReader(Protocol):
    async def get_closed_orders_stats(self) -> List[OrderStatRow]:
        """Return per-order revenue/expenses for all closed active orders."""
        ...
