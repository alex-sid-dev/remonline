from typing import Optional
from datetime import datetime
from uuid import uuid4

from src.application.errors._base import FieldError
from src.entities.orders.models import Order, OrderID, OrderUUID
from src.entities.orders.enum import OrderStatus
from src.entities.clients.models import ClientID
from src.entities.devices.models import DeviceID
from src.entities.employees.models import EmployeeID

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
        problem_description: Optional[str] = None,
        assigned_employee_id: Optional[EmployeeID] = None,
        status: OrderStatus | str = OrderStatus.NEW,
        price: Optional[float] = None,
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
        creator_id: Optional[EmployeeID] = None,
        assigned_employee_id: Optional[EmployeeID] = None,
        status: Optional[OrderStatus] = None,
        problem_description: Optional[str] = None,
        price: Optional[float] = None,
        is_active: Optional[bool] = None,
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
