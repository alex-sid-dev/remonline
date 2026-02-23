from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError, ConflictError, FieldError
from src.application.ports.brand_reader import BrandReader
from src.application.ports.client_reader import ClientReader
from src.application.ports.device_type_reader import DeviceTypeReader
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.brands.models import BrandUUID
from src.entities.clients.models import ClientUUID
from src.entities.clients.services import ClientService
from src.entities.device_types.models import DeviceTypeUUID
from src.entities.devices.services import DeviceService
from src.entities.employees.enum import EmployeePosition
from src.entities.employees.models import Employee, EmployeeUUID
from src.entities.orders.models import Order
from src.entities.orders.services import OrderService

logger = structlog.get_logger("create_order_with_client_and_device").bind(service="order")


@dataclass
class CreateOrderWithClientAndDeviceCommandResponse:
  order_uuid: UUID
  client_uuid: UUID
  device_uuid: UUID


@dataclass
class CreateOrderWithClientAndDeviceCommand:
  # Существующий клиент (если выбран по поиску)
  existing_client_uuid: Optional[UUID] = None

  # Данные нового клиента (если создаём)
  client_full_name: Optional[str] = None
  client_phone: Optional[str] = None
  client_email: Optional[str] = None
  client_telegram_nick: Optional[str] = None
  client_comment: Optional[str] = None
  client_address: Optional[str] = None

  # Данные устройства (всегда создаём новое устройство для заказа)
  device_type_uuid: UUID = None  # type: ignore[assignment]
  device_brand_uuid: Optional[UUID] = None
  device_model: str = ""
  device_serial_number: Optional[str] = None
  device_description: Optional[str] = None

  # Поля заказа
  assigned_employee_uuid: Optional[UUID] = None
  manager_uuid: Optional[UUID] = None
  status: str = "new"
  problem_description: Optional[str] = None
  price: Optional[float] = None


class CreateOrderWithClientAndDeviceCommandHandler(BaseCommandHandler):
  def __init__(
      self,
      transaction: Transaction,
      entity_saver: EntitySaver,
      client_service: ClientService,
      device_service: DeviceService,
      order_service: OrderService,
      client_reader: ClientReader,
      device_type_reader: DeviceTypeReader,
      brand_reader: BrandReader,
      employee_reader: EmployeeReader,
  ) -> None:
    self._transaction = transaction
    self._entity_saver = entity_saver
    self._client_service = client_service
    self._device_service = device_service
    self._order_service = order_service
    self._client_reader = client_reader
    self._device_type_reader = device_type_reader
    self._brand_reader = brand_reader
    self._employee_reader = employee_reader

  async def _resolve_client(self, data: CreateOrderWithClientAndDeviceCommand) -> "Client":
    # 1) Если пришёл existing_client_uuid — просто валидируем его наличие и используем
    if data.existing_client_uuid:
      client = await self._client_reader.read_by_uuid(ClientUUID(data.existing_client_uuid))
      if not client:
        raise EntityNotFoundError(message=f"Client with uuid {data.existing_client_uuid} not found")
      return client

    # 2) Иначе создаём нового клиента. Требуем минимум ФИО и телефон.
    if not data.client_full_name or not data.client_phone:
      raise FieldError(message="Для создания нового клиента необходимы full_name и phone.")

    existing_by_phone = await self._client_reader.read_by_phone(data.client_phone)
    if existing_by_phone:
      # Поведение совместимо с CreateClientCommand: не создаём дубликат по телефону
      raise ConflictError(message=f"Client with phone {data.client_phone} already exists")

    client = self._client_service.create_client(
      full_name=data.client_full_name,
      phone=data.client_phone,
      email=data.client_email,
      telegram_nick=data.client_telegram_nick,
      comment=data.client_comment,
      address=data.client_address,
    )
    self._entity_saver.add_one(client)
    await self._transaction.flush()  # чтобы client.id был присвоен до создания устройства
    return client

  async def _resolve_device(self, data: CreateOrderWithClientAndDeviceCommand, client: "Client") -> "Device":
    if not data.device_type_uuid:
      raise FieldError(message="device_type_uuid is required for new device.")
    if not data.device_brand_uuid or not data.device_model:
      raise FieldError(message="device_brand_uuid and device_model are required for new device.")

    device_type = await self._device_type_reader.read_by_uuid(DeviceTypeUUID(data.device_type_uuid))
    if not device_type:
      raise EntityNotFoundError(message=f"Device type with uuid {data.device_type_uuid} not found")

    brand = await self._brand_reader.read_by_uuid(BrandUUID(data.device_brand_uuid))
    if not brand:
      raise EntityNotFoundError(message=f"Brand with uuid {data.device_brand_uuid} not found")

    device = self._device_service.create_device(
      client_id=client.id,
      type_id=device_type.id,
      brand_id=brand.id,
      model=data.device_model,
      serial_number=data.device_serial_number,
      description=data.device_description,
    )
    self._entity_saver.add_one(device)
    return device

  async def _resolve_assigned_employee_id(self, data: CreateOrderWithClientAndDeviceCommand) -> Optional[int]:
    if not data.assigned_employee_uuid:
      return None
    employee = await self._employee_reader.read_by_uuid(EmployeeUUID(data.assigned_employee_uuid))
    if not employee:
      raise EntityNotFoundError(message=f"Employee with uuid {data.assigned_employee_uuid} not found")
    return employee.id

  async def _resolve_creator_id(self, data: CreateOrderWithClientAndDeviceCommand, current_employee: Employee) -> int:
    """
    Логика полностью повторяет CreateOrderCommand:
    - если передан manager_uuid — используем его; назначить менеджером заказа нельзя только мастера;
    - если заказ создаёт менеджер — он сам становится менеджером заказа;
    - иначе (админ/супервизор/мастер) — creator_id = current_employee.id.
    """
    creator_id = current_employee.id
    if data.manager_uuid:
      manager = await self._employee_reader.read_by_uuid(EmployeeUUID(data.manager_uuid))
      if not manager:
        raise EntityNotFoundError(message=f"Employee with uuid {data.manager_uuid} not found")
      if manager.position == EmployeePosition.MASTER:
        raise EntityNotFoundError(message="Назначить менеджером нельзя сотрудника с ролью мастер.")
      creator_id = manager.id
    elif getattr(current_employee, "position", None) == EmployeePosition.MANAGER:
      creator_id = current_employee.id
    return creator_id

  async def run(
      self,
      data: CreateOrderWithClientAndDeviceCommand,
      current_employee: Employee,
  ) -> CreateOrderWithClientAndDeviceCommandResponse:
    # 1) Разруливаем клиента (существующий или новый)
    client = await self._resolve_client(data)

    # 2) Создаём устройство для клиента
    device = await self._resolve_device(data, client)

    # Flush, чтобы клиенту и устройству присвоились id до вставки заказа
    await self._transaction.flush()

    # 3) Назначенный инженер
    assigned_employee_id = await self._resolve_assigned_employee_id(data)

    # 4) Менеджер / creator_id
    creator_id = await self._resolve_creator_id(data, current_employee)

    # 5) Создаём заказ
    order: Order = self._order_service.create_order(
      client_id=client.id,
      device_id=device.id,
      creator_id=creator_id,
      problem_description=data.problem_description,
      assigned_employee_id=assigned_employee_id,
      status=data.status,
      price=data.price,
    )
    self._entity_saver.add_one(order)

    # 6) Коммитим все три сущности одним транзакционным контекстом
    await self._transaction.commit()

    logger.info(
      "Order with client and device created successfully",
      order_uuid=str(order.uuid),
      client_uuid=str(client.uuid),
      device_uuid=str(device.uuid),
    )
    return CreateOrderWithClientAndDeviceCommandResponse(
      order_uuid=order.uuid,
      client_uuid=client.uuid,
      device_uuid=device.uuid,
    )

