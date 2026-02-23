from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.entities.orders.enum import OrderStatus


class CreateOrderWithClientAndDeviceSchema(BaseModel):
  # Существующий клиент (если выбран по поиску)
  existing_client_uuid: Optional[UUID] = None

  # Новый клиент (если создаём)
  client_full_name: Optional[str] = None
  client_phone: Optional[str] = None
  client_email: Optional[str] = None
  client_telegram_nick: Optional[str] = None
  client_comment: Optional[str] = None
  client_address: Optional[str] = None

  # Устройство (новое)
  device_type_uuid: UUID
  device_brand_uuid: UUID
  device_model: str
  device_serial_number: Optional[str] = None
  device_description: Optional[str] = None

  # Заказ
  assigned_employee_uuid: Optional[UUID] = None
  manager_uuid: Optional[UUID] = None
  status: OrderStatus = OrderStatus.NEW
  problem_description: Optional[str] = None
  price: Optional[float] = None

