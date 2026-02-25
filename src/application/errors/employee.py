from dataclasses import dataclass

from src.application.errors._base import EntityNotFoundError


@dataclass(eq=False)
class EmployeeNotFoundError(EntityNotFoundError):
    message: str = "Employee is not found"
