import re
from typing import Optional
from pydantic import BaseModel, field_validator, Field
from src.entities.employees.enum import EmployeePosition

class EmployeeBaseSchema(BaseModel):
    """Базовая схема с общей логикой"""
    full_name: Optional[str] = Field(None, description="ФИО сотрудника", examples=["Иванов Иван Иванович"])
    phone: Optional[str] = Field(None, description="Номер телефона", examples=["+79001234567"])
    position: Optional[EmployeePosition] = Field(None, description="Роль сотрудника")
    salary: Optional[float] = Field(None, ge=0, description="Зарплата в месяц")
    profit_percent: Optional[float] = Field(None, ge=0, le=100, description="Процент от прибыли")

    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        pattern = r"^\+\d{10,15}$"
        if not re.match(pattern, v.strip()):
            raise ValueError("Номер должен начинаться с '+' и содержать от 10 до 15 цифр")
        return v.strip()

class CreateEmployeeSchema(EmployeeBaseSchema):
    """Схема создания: все поля обязательны"""
    full_name: str = Field(..., description="ФИО сотрудника")
    phone: str = Field(..., description="Номер телефона")
    position: EmployeePosition = Field(..., description="Роль сотрудника")

