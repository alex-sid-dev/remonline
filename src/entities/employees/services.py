from typing import cast
from uuid import UUID

from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee
from src.entities.organizations.models import OrganizationID
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
        organization_id: OrganizationID,
        salary: float | None = None,
        profit_percent: float | None = None,
    ) -> Employee:
        return Employee(
            id=cast("EmployeeID", None),  # noqa: F821
            uuid=uuid,
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            is_active=is_active,
            position=position,
            organization_id=organization_id,
            salary=salary,
            profit_percent=profit_percent,
        )

    @staticmethod
    def update_employee(
        employee: Employee,
        phone: str | None = None,
        full_name: str | None = None,
        position: EmployeePosition | None = None,
        salary: float | None = None,
        profit_percent: float | None = None,
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
