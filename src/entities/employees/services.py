from typing import Optional, cast
from uuid import UUID

from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee
from src.entities.users.models import UserID


class EmployeeService:

    @staticmethod
    def create_employee(
            user_id: UserID,
            phone: str,
            full_name: str,
            is_active: bool,
            position: EmployeePosition,
            uuid: UUID,
            salary: Optional[float] = None,
            profit_percent: Optional[float] = None,
    ) -> Employee:
        return Employee(
            id=cast("EmployeeID", None),  # noqa: F821
            uuid=uuid,
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            is_active=is_active,
            position=position,
            salary=salary,
            profit_percent=profit_percent,
        )

    @staticmethod
    def update_employee(
            employee: Employee,
            phone: Optional[str] = None,
            full_name: Optional[str] = None,
            position: Optional[EmployeePosition] = None,
            salary: Optional[float] = None,
            profit_percent: Optional[float] = None,
    ) -> Employee:
        if phone is not None:
            employee.phone = phone
        if full_name is not None:
            employee.full_name = full_name
        if position is not None:
            employee.position = position
        if salary is not None:
            employee.salary = salary
        if profit_percent is not None:
            employee.profit_percent = profit_percent
        return employee
