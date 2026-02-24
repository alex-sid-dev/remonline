from uuid import uuid4

from src.entities.employees.models import EmployeeID
from src.entities.orders.models import OrderID
from src.entities.works.models import Work, WorkUUID


class WorkService:
    def create_work(
        self,
        order_id: OrderID,
        title: str,
        employee_id: EmployeeID | None = None,
        description: str | None = None,
        price: float | None = None,
        qty: int = 1,
    ) -> Work:
        return Work(
            id=None,  # type: ignore
            uuid=WorkUUID(uuid4()),
            order_id=order_id,
            title=title,
            employee_id=employee_id,
            description=description,
            price=price,
            qty=qty,
            is_active=True,
        )

    def update_work(
        self,
        work: Work,
        title: str | None = None,
        employee_id: EmployeeID | None = None,
        description: str | None = None,
        price: float | None = None,
        qty: int | None = None,
        is_active: bool | None = None,
    ) -> Work:
        if title is not None:
            work.title = title
        if employee_id is not None:
            work.employee_id = employee_id
        if description is not None:
            work.description = description
        if price is not None:
            work.price = price
        if qty is not None:
            work.qty = qty
        if is_active is not None:
            work.is_active = is_active
        return work
