from typing import Final, List

import structlog
from sqlalchemy import select, func, literal
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.statistics_reader import OrderStatRow, StatisticsReader
from src.entities.orders.enum import OrderStatus
from src.infra.models.orders import orders_table
from src.infra.models.works import works_table
from src.infra.models.order_parts import order_parts_table


class StatisticsReaderAdapter(StatisticsReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session: Final = session
        self._logger = structlog.get_logger("db").bind(service="db", entity="statistics")

    async def get_closed_orders_stats(self) -> List[OrderStatRow]:
        self._logger.info("Reading closed orders statistics")

        works_sub = (
            select(
                works_table.c.order_id,
                func.coalesce(
                    func.sum(works_table.c.price * works_table.c.qty), literal(0)
                ).label("works_revenue"),
            )
            .where(works_table.c.is_active.is_(True))
            .group_by(works_table.c.order_id)
            .subquery("ws")
        )

        parts_sub = (
            select(
                order_parts_table.c.order_id,
                func.coalesce(
                    func.sum(order_parts_table.c.price * order_parts_table.c.qty), literal(0)
                ).label("parts_expenses"),
            )
            .group_by(order_parts_table.c.order_id)
            .subquery("ps")
        )

        stmt = (
            select(
                orders_table.c.order_id,
                orders_table.c.creator_id,
                orders_table.c.assigned_employee_id,
                func.coalesce(works_sub.c.works_revenue, literal(0)).label("works_revenue"),
                func.coalesce(parts_sub.c.parts_expenses, literal(0)).label("parts_expenses"),
            )
            .outerjoin(works_sub, orders_table.c.order_id == works_sub.c.order_id)
            .outerjoin(parts_sub, orders_table.c.order_id == parts_sub.c.order_id)
            .where(
                orders_table.c.status == OrderStatus.CLOSED.value,
                orders_table.c.is_active.is_(True),
            )
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        stats = [
            OrderStatRow(
                order_id=r.order_id,
                creator_id=r.creator_id,
                assigned_employee_id=r.assigned_employee_id,
                works_revenue=float(r.works_revenue or 0),
                parts_expenses=float(r.parts_expenses or 0),
            )
            for r in rows
        ]
        self._logger.info("Closed orders statistics loaded", count=len(stats))
        return stats
