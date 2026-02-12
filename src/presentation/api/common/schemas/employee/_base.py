import re
from typing import Optional
from pydantic import BaseModel, field_validator, Field
from src.entities.employees.enum import EmployeePosition

class EmployeeBaseSchema(BaseModel):
    """Базовая схема с общей логикой"""
    full_name: Optional[str] = Field(None, description="ФИО сотрудника", examples=["Иванов Иван Иванович"])
    phone: Optional[str] = Field(None, description="Номер телефона", examples=["+79001234567"])
    position: Optional[EmployeePosition] = Field(None, description="Роль сотрудника")

    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        pattern = r"^\+\d{10,15}$"
        if not re.match(pattern, v):
            raise ValueError("Номер должен начинаться с '+' и содержать от 10 до 15 цифр")
        return v

class CreateEmployeeSchema(EmployeeBaseSchema):
    """Схема создания: все поля обязательны"""
    full_name: str = Field(..., description="ФИО сотрудника")
    phone: str = Field(..., description="Номер телефона")
    position: EmployeePosition = Field(..., description="Роль сотрудника")

