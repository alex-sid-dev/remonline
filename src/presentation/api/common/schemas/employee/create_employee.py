from pydantic import Field

from src.entities.employees.enum import EmployeePosition
from src.presentation.api.common.schemas.employee._base import EmployeeBaseSchema


class CreateEmployeeSchema(EmployeeBaseSchema):
    """Схема создания: все поля обязательны"""
    user_id: int = Field(..., description="user_id сотрудника")
    full_name: str = Field(..., description="ФИО сотрудника")
    phone: str = Field(..., description="Номер телефона")
    position: EmployeePosition = Field(..., description="Роль сотрудника")

