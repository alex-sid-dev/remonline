from uuid import UUID
from pydantic import Field, field_validator

from src.entities.employees.enum import EmployeePosition

from src.presentation.api.common.schemas.employee._base import EmployeeBaseSchema
from src.presentation.api.common.validators.phone import validate_phone


class CreateEmployeeSchema(EmployeeBaseSchema):
    """Схема создания: все поля обязательны"""
    user_uuid: UUID = Field(..., description="UUID пользователя сотрудника")
    full_name: str = Field(..., description="ФИО сотрудника")
    phone: str = Field(..., description="Номер телефона")
    position: EmployeePosition = Field(..., description="Роль сотрудника")

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: str) -> str:
        return validate_phone(v)

