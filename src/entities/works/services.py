from typing import Optional
from uuid import uuid4
from src.entities.works.models import Work, WorkID, WorkUUID
from src.entities.orders.models import OrderID
from src.entities.employees.models import EmployeeID

class WorkService:
    def create_work(
        self,
        order_id: OrderID,
        title: str,
        employee_id: Optional[EmployeeID] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
    ) -> Work:
        return Work(
            id=None,  # type: ignore
            uuid=WorkUUID(uuid4()),
            order_id=order_id,
            title=title,
            employee_id=employee_id,
            description=description,
            price=price,
            is_active=True,
        )

    def update_work(
        self,
        work: Work,
        title: Optional[str] = None,
        employee_id: Optional[EmployeeID] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        is_active: Optional[bool] = None,
    ) -> Work:
        if title is not None:
            work.title = title
        if employee_id is not None:
            work.employee_id = employee_id
        if description is not None:
            work.description = description
        if price is not None:
            work.price = price
        if is_active is not None:
            work.is_active = is_active
        return work
