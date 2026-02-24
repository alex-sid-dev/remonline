from dataclasses import dataclass

from src.application.errors._base import ConflictError, EntityNotFoundError


@dataclass(eq=False)
class EmployeeNotFoundError(EntityNotFoundError):
    message: str = "Employee is not found"


@dataclass(eq=False)
class EmployeeIsAlreadyExist(ConflictError):
    message: str = "Employee is already exist"
