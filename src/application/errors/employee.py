from dataclasses import dataclass

from src.application.errors._base import EntityNotFoundError, ConflictError


@dataclass
class EmployeeNotFoundError(EntityNotFoundError):

    @property
    def message(self) -> str:
        return "Employee is not found"

@dataclass
class EmployeeIsAlreadyExist(ConflictError):

    @property
    def message(self) -> str:
        return "Employee is already exist"