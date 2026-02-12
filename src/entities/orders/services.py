from typing import Optional
from datetime import datetime
from uuid import uuid4
from src.entities.orders.models import Order, OrderID, OrderUUID
from src.entities.clients.models import ClientID
from src.entities.devices.models import DeviceID
from src.entities.employees.models import EmployeeID

class OrderService:
    def create_order(
        self,
        client_id: ClientID,
        device_id: DeviceID,
        creator_id: EmployeeID,
        problem_description: Optional[str] = None,
        comment: Optional[str] = None,
        assigned_employee_id: Optional[EmployeeID] = None,
        status: str = "new",
        price: Optional[float] = None,
    ) -> Order:
        now = datetime.now()
        return Order(
            id=None,  # type: ignore
            uuid=OrderUUID(uuid4()),
            client_id=client_id,
            device_id=device_id,
            creator_id=creator_id,
            assigned_employee_id=assigned_employee_id,
            status=status,
            problem_description=problem_description,
            comment=comment,
            price=price,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def update_order(
        self,
        order: Order,
        assigned_employee_id: Optional[EmployeeID] = None,
        status: Optional[str] = None,
        problem_description: Optional[str] = None,
        comment: Optional[str] = None,
        price: Optional[float] = None,
        is_active: Optional[bool] = None,
    ) -> Order:
        if assigned_employee_id is not None:
            order.assigned_employee_id = assigned_employee_id
        if status is not None:
            order.status = status
        if problem_description is not None:
            order.problem_description = problem_description
        if comment is not None:
            order.comment = comment
        if price is not None:
            order.price = price
        if is_active is not None:
            order.is_active = is_active
        
        order.updated_at = datetime.now()
        return order
