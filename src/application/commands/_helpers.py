from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from src.application.errors._base import EntityNotFoundError, FieldError
from src.application.ports.employee_reader import EmployeeReader
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee, EmployeeUUID


async def ensure_exists[T](
    reader_method: Callable[..., Awaitable[T | None]],
    identifier: Any,
    entity_name: str,
) -> T:
    entity = await reader_method(identifier)
    if entity is None:
        raise EntityNotFoundError(f"{entity_name} not found")
    return entity


async def resolve_employee_id(
    employee_reader: EmployeeReader,
    employee_uuid: UUID | None,
) -> int | None:
    if employee_uuid is None:
        return None
    emp = await ensure_exists(employee_reader.read_by_uuid, EmployeeUUID(employee_uuid), "Employee")
    return emp.id


async def resolve_order_creator_id(
    employee_reader: EmployeeReader,
    manager_uuid: UUID | None,
    current_employee: Employee,
) -> int:
    creator_id = current_employee.id
    if manager_uuid:
        manager = await ensure_exists(
            employee_reader.read_by_uuid, EmployeeUUID(manager_uuid), "Employee"
        )
        if manager.position == EmployeePosition.MASTER:
            raise FieldError(message="Назначить менеджером нельзя сотрудника с ролью мастер.")
        creator_id = manager.id
    elif current_employee.position == EmployeePosition.MANAGER:
        creator_id = current_employee.id
    return creator_id
