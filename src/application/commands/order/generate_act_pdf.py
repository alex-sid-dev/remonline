from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import structlog
from jinja2 import Environment, FileSystemLoader

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.entities.employees.models import Employee
from src.entities.orders.models import OrderUUID
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("generate_act").bind(service="order")

TEMPLATES_DIR = Path(__file__).resolve().parents[4] / "templates"


@dataclass
class GenerateActPdfCommand:
    uuid: UUID


class GenerateActPdfCommandHandler(BaseCommandHandler):
    def __init__(self, order_reader: OrderReader) -> None:
        self._order_reader = order_reader

    async def run(self, data: GenerateActPdfCommand, current_employee: Employee) -> str:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.uuid))
        if not order:
            raise EntityNotFoundError(message=f"Order with uuid {data.uuid} not found")

        works_data = []
        works_total = 0.0
        for w in getattr(order, "works", []):
            price = w.price or 0.0
            qty = w.qty or 1
            total = price * qty
            works_total += total
            employee = getattr(w, "employee", None)
            works_data.append({
                "title": w.title,
                "employee_name": employee.full_name if employee else "—",
                "qty": qty,
                "price": price,
                "total": total,
            })

        parts_data = []
        parts_total = 0.0
        for op in getattr(order, "parts", []):
            part = getattr(op, "part_info", None)
            price = op.price if op.price is not None else (part.price if part and part.price else 0.0)
            qty = op.qty or 1
            total = price * qty
            parts_total += total
            parts_data.append({
                "name": part.name if part else "—",
                "sku": part.sku if part else None,
                "qty": qty,
                "price": price,
                "total": total,
            })

        creator = getattr(order, "creator", None)
        assigned = getattr(order, "assigned_employee", None)
        client = getattr(order, "client", None)
        device = getattr(order, "device", None)

        created_at = order.created_at.strftime("%d.%m.%Y") if order.created_at else "—"

        context = {
            "order": {"id": order.id, "created_at": created_at},
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
            "engineer_name": assigned.full_name if assigned else "Не назначен",
            "works": works_data,
            "parts": parts_data,
            "problem_description": order.problem_description,
            "works_total": works_total,
            "parts_total": parts_total,
            "grand_total": works_total + parts_total,
        }

        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
        template = env.get_template("act.html")
        return template.render(**context)
