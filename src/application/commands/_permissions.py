from src.application.errors._base import PermissionDeniedError
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee

ADMIN_CAN_MODIFY = {EmployeePosition.MASTER, EmployeePosition.MANAGER}


def assert_can_assign_supervisor(caller: Employee) -> None:
    if caller.position != EmployeePosition.SUPERVISOR:
        raise PermissionDeniedError(message="Только супервизор может назначать роль «супервизор».")


def assert_can_modify_target(caller: Employee, target: Employee) -> None:
    if caller.position == EmployeePosition.ADMIN and target.position not in ADMIN_CAN_MODIFY:
        raise PermissionDeniedError(
            message="Админ может редактировать только мастеров и менеджеров."
        )


def assert_can_change_salary(caller: Employee) -> None:
    if caller.position != EmployeePosition.SUPERVISOR:
        raise PermissionDeniedError(
            message="Только супервизор может менять зарплату и процент от прибыли."
        )
