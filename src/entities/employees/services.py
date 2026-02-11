from typing import cast

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
    ) -> Employee:
        return Employee(
            oid=cast("EmployeeID", None),  # noqa: F821
            ouuid=cast("EmployeeUUID", None),  # noqa: F821
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            is_active=is_active,
            position=position,
        )

    @staticmethod
    def update_employee(
            employee: Employee,
            phone: str = None,
            full_name: str = None,
            position: EmployeePosition = None,
    ) -> Employee:
        if phone is not None:
            employee.phone = phone
        if full_name is not None:
            employee.full_name = full_name
        if position is not None:
            employee.position = position
        return employee
