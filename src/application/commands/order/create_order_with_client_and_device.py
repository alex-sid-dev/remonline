from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

import structlog

from src.application.commands._helpers import (
    ensure_exists,
    resolve_employee_id,
    resolve_order_creator_id,
)
from src.application.errors._base import ConflictError, FieldError
from src.application.ports.brand_reader import BrandReader
from src.application.ports.client_reader import ClientReader
from src.application.ports.device_type_reader import DeviceTypeReader
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.brands.models import BrandUUID
from src.entities.clients.models import ClientUUID
from src.entities.clients.services import ClientService
from src.entities.device_types.models import DeviceTypeUUID
from src.entities.devices.services import DeviceService
from src.entities.employees.models import Employee
from src.entities.orders.models import Order
from src.entities.orders.services import OrderService

if TYPE_CHECKING:
    from src.entities.clients.models import Client
    from src.entities.devices.models import Device

logger = structlog.get_logger("create_order_with_client_and_device").bind(service="order")


@dataclass(frozen=True, slots=True)
class CreateOrderWithClientAndDeviceCommandResponse:
    order_uuid: UUID
    client_uuid: UUID
    device_uuid: UUID


@dataclass(frozen=True, slots=True)
class CreateOrderWithClientAndDeviceCommand:
    # Существующий клиент (если выбран по поиску)
    existing_client_uuid: UUID | None = None

    # Данные нового клиента (если создаём)
    client_full_name: str | None = None
    client_phone: str | None = None
    client_email: str | None = None
    client_telegram_nick: str | None = None
    client_comment: str | None = None
    client_address: str | None = None

    # Данные устройства (всегда создаём новое устройство для заказа)
    device_type_uuid: UUID | None = None
    device_brand_uuid: UUID | None = None
    device_model: str = ""
    device_serial_number: str | None = None
    device_description: str | None = None

    # Поля заказа
    assigned_employee_uuid: UUID | None = None
    manager_uuid: UUID | None = None
    status: str = "new"
    problem_description: str | None = None
    price: float | None = None


class CreateOrderWithClientAndDeviceCommandHandler:
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

    async def _resolve_client(self, data: CreateOrderWithClientAndDeviceCommand) -> Client:
        if data.existing_client_uuid:
            return await ensure_exists(
                self._client_reader.read_by_uuid, ClientUUID(data.existing_client_uuid),
                f"Client with uuid {data.existing_client_uuid}",
            )

        if not data.client_full_name or not data.client_phone:
            raise FieldError(message="Для создания нового клиента необходимы full_name и phone.")

        existing_by_phone = await self._client_reader.read_by_phone(data.client_phone)
        if existing_by_phone:
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
        await self._transaction.flush()
        return client

    async def _resolve_device(
        self, data: CreateOrderWithClientAndDeviceCommand, client: Client
    ) -> Device:
        if not data.device_type_uuid:
            raise FieldError(message="device_type_uuid is required for new device.")
        if not data.device_brand_uuid or not data.device_model:
            raise FieldError(
                message="device_brand_uuid and device_model are required for new device."
            )

        device_type = await ensure_exists(
            self._device_type_reader.read_by_uuid, DeviceTypeUUID(data.device_type_uuid),
            f"Device type with uuid {data.device_type_uuid}",
        )
        brand = await ensure_exists(
            self._brand_reader.read_by_uuid, BrandUUID(data.device_brand_uuid),
            f"Brand with uuid {data.device_brand_uuid}",
        )

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

    async def run(
        self,
        data: CreateOrderWithClientAndDeviceCommand,
        current_employee: Employee,
    ) -> CreateOrderWithClientAndDeviceCommandResponse:
        client = await self._resolve_client(data)
        device = await self._resolve_device(data, client)
        await self._transaction.flush()

        assigned_employee_id = await resolve_employee_id(
            self._employee_reader, data.assigned_employee_uuid
        )
        creator_id = await resolve_order_creator_id(
            self._employee_reader, data.manager_uuid, current_employee
        )

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
