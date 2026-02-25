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

logger = structlog.get_logger("generate_receipt").bind(service="order")


@dataclass(frozen=True, slots=True)
class GenerateReceiptHtmlCommand:
    uuid: UUID


class GenerateReceiptHtmlCommandHandler:
    def __init__(
        self,
        order_reader: OrderReader,
        organization_reader: OrganizationReader,
    ) -> None:
        self._order_reader = order_reader
        self._organization_reader = organization_reader

    async def run(self, data: GenerateReceiptHtmlCommand, current_employee: Employee) -> str:
        order = await ensure_exists(
            self._order_reader.read_by_uuid, OrderUUID(data.uuid),
            f"Order with uuid {data.uuid}",
        )

        org = await self._organization_reader.get_single()
        context = build_order_base_context(order)
        context["organization"] = build_organization_context(org)

        return render_template("receipt.html", **context)
