from collections.abc import Iterable, Sequence
from datetime import datetime
from uuid import uuid4

from src.application.errors._base import FieldError
from src.entities.clients.models import ClientID
from src.entities.devices.models import DeviceID
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import EmployeeID
from src.entities.order_parts.models import OrderPart
from src.entities.orders.enum import OrderStatus
from src.entities.orders.models import Order, OrderUUID
from src.entities.works.models import Work


class OrderService:
    def _normalize_status(self, status: OrderStatus | str | None) -> OrderStatus:
        """Приводит статус к OrderStatus, принимая как enum, так и строки (в любом регистре)."""
        if status is None:
            return OrderStatus.NEW

        if isinstance(status, OrderStatus):
            return status

        # Пытаемся сначала по значению (value), затем по имени (name, в верхнем регистре)
        try:
            return OrderStatus(status)  # type: ignore[arg-type]
        except ValueError:
            upper = str(status).upper()
            for s in OrderStatus:
                if s.name == upper:
                    return s
            valid = ", ".join(s.value for s in OrderStatus)
            raise FieldError(message=f"Недопустимый статус заказа: '{status}'. Допустимые: {valid}")

    def create_order(
        self,
        client_id: ClientID,
        device_id: DeviceID,
        creator_id: EmployeeID,
        problem_description: str | None = None,
        assigned_employee_id: EmployeeID | None = None,
        status: OrderStatus | str = OrderStatus.NEW,
        price: float | None = None,
    ) -> Order:
        now = datetime.now()
        normalized_status = self._normalize_status(status)

        return Order(
            id=None,  # type: ignore
            uuid=OrderUUID(uuid4()),
            client_id=client_id,
            device_id=device_id,
            creator_id=creator_id,
            assigned_employee_id=assigned_employee_id,
            status=normalized_status,
            problem_description=problem_description,
            price=price,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def update_order(
        self,
        order: Order,
        creator_id: EmployeeID | None = None,
        assigned_employee_id: EmployeeID | None = None,
        status: OrderStatus | None = None,
        problem_description: str | None = None,
        price: float | None = None,
        is_active: bool | None = None,
    ) -> Order:
        if creator_id is not None:
            order.creator_id = creator_id
        if assigned_employee_id is not None:
            order.assigned_employee_id = assigned_employee_id
        if status is not None:
            order.status = self._normalize_status(status)
        if problem_description is not None:
            order.problem_description = problem_description
        if price is not None:
            order.price = price
        if is_active is not None:
            order.is_active = is_active

        order.updated_at = datetime.now()
        return order

    @staticmethod
    def assign_engineer_to_unassigned_works(works: list, employee_id: EmployeeID) -> list:
        """Assign engineer to works that don't have one."""
        updated = []
        for work in works:
            if work.employee_id is None:
                work.employee_id = employee_id
                updated.append(work)
        return updated

    # --- Расчёт цены заказа и доступных статусов ---

    @staticmethod
    def calculate_total_price(order: Order) -> float:
        """
        Считает итоговую стоимость заказа по работам и запчастям.
        Логика совпадает с тем, что сейчас делает фронтенд.
        """
        total = 0.0

        works: Iterable[Work] = getattr(order, "works", []) or []
        for work in works:
            price = work.price or 0.0
            qty = work.qty or 1
            total += price * qty

        parts: Iterable[OrderPart] = getattr(order, "parts", []) or []
        for op in parts:
            qty = op.qty or 0
            unit_price = op.price
            if unit_price is None:
                part_info = getattr(op, "part_info", None)
                unit_price = getattr(part_info, "price", 0.0)
            total += (unit_price or 0.0) * qty

        return total

    @staticmethod
    def calculate_total_price_from_works_parts(
        works: Sequence[Work], parts: Sequence[OrderPart]
    ) -> float:
        """Считает итоговую стоимость по спискам работ и запчастей (для пересчёта при update)."""
        total = 0.0
        for work in works:
            total += (work.price or 0.0) * (work.qty or 1)
        for op in parts:
            unit_price = op.price
            if unit_price is None:
                part_info = getattr(op, "part_info", None)
                unit_price = getattr(part_info, "price", 0.0)
            total += (unit_price or 0.0) * (op.qty or 0)
        return total

    @staticmethod
    def allowed_statuses_for_position(position: EmployeePosition) -> list[OrderStatus]:
        """
        Возвращает список статусов, которые пользователь с данной ролью может устанавливать.
        Сейчас логика такая же, как на фронте:
        - supervisor: может ставить любые статусы
        - остальные роли: все, кроме 'closed'
        """
        if position == EmployeePosition.SUPERVISOR:
            return list(OrderStatus)

        return [s for s in OrderStatus if s is not OrderStatus.CLOSED]
