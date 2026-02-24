from uuid import UUID

from pydantic import BaseModel
from src.entities.orders.enum import OrderStatus


class CreateOrderWithClientAndDeviceSchema(BaseModel):
    # Существующий клиент (если выбран по поиску)
    existing_client_uuid: UUID | None = None

    # Новый клиент (если создаём)
    client_full_name: str | None = None
    client_phone: str | None = None
    client_email: str | None = None
    client_telegram_nick: str | None = None
    client_comment: str | None = None
    client_address: str | None = None

    # Устройство (новое)
    device_type_uuid: UUID
    device_brand_uuid: UUID
    device_model: str
    device_serial_number: str | None = None
    device_description: str | None = None

    # Заказ
    assigned_employee_uuid: UUID | None = None
    manager_uuid: UUID | None = None
    status: OrderStatus = OrderStatus.NEW
    problem_description: str | None = None
    price: float | None = None
