from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands.order._document_helpers import (
    build_order_base_context,
    build_organization_context,
    render_template,
)
from src.application.ports.order_reader import OrderReader
from src.application.ports.organization_reader import OrganizationReader
from src.entities.employees.models import Employee
from src.entities.orders.models import OrderUUID

logger = structlog.get_logger("generate_act").bind(service="order")


@dataclass(frozen=True, slots=True)
class GenerateActPdfCommand:
    uuid: UUID


class GenerateActPdfCommandHandler:
    def __init__(
        self,
        order_reader: OrderReader,
        organization_reader: OrganizationReader,
    ) -> None:
        self._order_reader = order_reader
        self._organization_reader = organization_reader

    async def run(self, data: GenerateActPdfCommand, current_employee: Employee) -> str:
        order = await ensure_exists(
            self._order_reader.read_by_uuid, OrderUUID(data.uuid),
            f"Order with uuid {data.uuid}",
        )

        org = await self._organization_reader.get_single()

        works_data = []
        works_total = 0.0
        for w in getattr(order, "works", []):
            price = w.price or 0.0
            qty = w.qty or 1
            total = price * qty
            works_total += total
            employee = getattr(w, "employee", None)
            works_data.append(
                {
                    "title": w.title,
                    "employee_name": employee.full_name if employee else "—",
                    "qty": qty,
                    "price": price,
                    "total": total,
                }
            )

        parts_data = []
        parts_total = 0.0
        for op in getattr(order, "parts", []):
            part = getattr(op, "part_info", None)
            price = (
                op.price if op.price is not None else (part.price if part and part.price else 0.0)
            )
            qty = op.qty or 1
            total = price * qty
            parts_total += total
            parts_data.append(
                {
                    "name": part.name if part else "—",
                    "sku": part.sku if part else None,
                    "qty": qty,
                    "price": price,
                    "total": total,
                }
            )

        assigned = getattr(order, "assigned_employee", None)
        context = build_order_base_context(order)
        context.update(
            organization=build_organization_context(org),
            engineer_name=assigned.full_name if assigned else "Не назначен",
            works=works_data,
            parts=parts_data,
            works_total=works_total,
            parts_total=parts_total,
            grand_total=works_total + parts_total,
        )

        return render_template("act.html", **context)
