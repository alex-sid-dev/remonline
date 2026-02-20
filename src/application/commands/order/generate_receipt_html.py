from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import structlog
from jinja2 import Environment, FileSystemLoader

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.application.ports.organization_reader import OrganizationReader
from src.entities.employees.models import Employee
from src.entities.orders.models import OrderUUID
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("generate_receipt").bind(service="order")

TEMPLATES_DIR = Path(__file__).resolve().parents[4] / "templates"


@dataclass
class GenerateReceiptHtmlCommand:
    uuid: UUID


class GenerateReceiptHtmlCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        order_reader: OrderReader,
        organization_reader: OrganizationReader,
    ) -> None:
        self._order_reader = order_reader
        self._organization_reader = organization_reader

    async def run(self, data: GenerateReceiptHtmlCommand, current_employee: Employee) -> str:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.uuid))
        if not order:
            raise EntityNotFoundError(message=f"Order with uuid {data.uuid} not found")

        org = await self._organization_reader.get_single()
        organization = (
            {
                "name": org.name,
                "inn": org.inn,
                "address": org.address,
                "kpp": org.kpp,
                "bank_account": org.bank_account,
                "corr_account": org.corr_account,
                "bik": org.bik,
            }
            if org
            else None
        )

        creator = getattr(order, "creator", None)
        client = getattr(order, "client", None)
        device = getattr(order, "device", None)

        created_at = order.created_at.strftime("%d.%m.%Y") if order.created_at else "—"

        context = {
            "order": {"id": order.id, "created_at": created_at},
            "organization": organization,
            "client": {
                "full_name": client.full_name if client else "—",
                "phone": client.phone if client else None,
                "address": client.address if client else None,
            },
            "device": {
                "brand": device.brand if device else "—",
                "model": device.model if device else "—",
                "serial_number": device.serial_number if device else None,
            },
            "manager_name": creator.full_name if creator else "Не назначен",
            "problem_description": order.problem_description,
        }

        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
        template = env.get_template("receipt.html")
        return template.render(**context)
