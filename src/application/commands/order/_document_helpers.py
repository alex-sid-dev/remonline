from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).resolve().parents[4] / "templates"

_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)


def build_organization_context(org: Any) -> dict[str, Any] | None:
    if not org:
        return None
    return {
        "name": org.name,
        "inn": org.inn,
        "address": org.address,
        "kpp": org.kpp,
        "bank_account": org.bank_account,
        "corr_account": org.corr_account,
        "bik": org.bik,
    }


def build_order_base_context(order: Any) -> dict[str, Any]:
    creator = getattr(order, "creator", None)
    client = getattr(order, "client", None)
    device = getattr(order, "device", None)

    created_at = order.created_at.strftime("%d.%m.%Y") if order.created_at else "—"

    return {
        "order": {"id": order.id, "created_at": created_at},
        "client": {
            "full_name": client.full_name if client else "—",
            "phone": client.phone if client else None,
            "address": client.address if client else None,
        },
        "device": {
            "brand": (device.brand.name if getattr(device, "brand", None) else "—")
            if device
            else "—",
            "model": device.model if device else "—",
            "serial_number": device.serial_number if device else None,
        },
        "manager_name": creator.full_name if creator else "Не назначен",
        "problem_description": order.problem_description,
    }


def render_template(template_name: str, **context: Any) -> str:
    template = _env.get_template(template_name)
    return template.render(**context)
