from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import structlog
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from src.application.commands._helpers import ensure_exists
from src.application.ports.order_reader import OrderReader
from src.entities.employees.models import Employee
from src.entities.orders.enum import OrderStatus
from src.entities.orders.models import OrderUUID
from src.entities.orders.services import OrderService

logger = structlog.get_logger("read_order").bind(service="order")


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Позволяет работать с объектами SQLAlchemy


class ClientShortResponse(BaseResponse):
    full_name: str
    phone: str | None = None
    address: str | None = None


class DeviceShortResponse(BaseResponse):
    model: str
    brand: str | None = None
    serial_number: str | None = None

    @field_validator("brand", mode="before")
    @classmethod
    def brand_to_str(cls, v):  # noqa: N805
        if v is None:
            return None
        if isinstance(v, str):
            return v
        return getattr(v, "name", None)


class EmployeeShortResponse(BaseResponse):
    uuid: UUID
    full_name: str


class OrderCommentResponse(BaseResponse):
    text: str = Field(validation_alias=AliasChoices("comment", "text"))  # ORM has .comment
    created_at: datetime
    creator: EmployeeShortResponse | None = None  # кто оставил комментарий


class PaymentResponse(BaseResponse):
    uuid: UUID
    amount: float
    payment_method: str
    created_at: datetime


class PartShortResponse(BaseResponse):
    uuid: UUID
    name: str
    sku: str | None = None
    price: float | None = None


class OrderPartResponse(BaseResponse):
    uuid: UUID
    part_id: int
    qty: int
    price: float | None = None
    part_info: PartShortResponse | None = None  # Если добавите маппинг выше


class WorkResponse(BaseResponse):
    uuid: UUID
    title: str
    description: str | None = None
    price: float | None = None
    qty: int = 1
    employee: EmployeeShortResponse | None = None  # Кто выполнял работу


# --- Основная схема ответа ---


class ReadOrderOneResponse(BaseResponse):
    id: int
    uuid: UUID
    status: str
    problem_description: str | None = None
    comment: str | None = None
    price: float | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    # Вложенные сущности (автоподгруженные)
    client: ClientShortResponse
    device: DeviceShortResponse
    creator: EmployeeShortResponse | None = None
    assigned_employee: EmployeeShortResponse | None = None

    # Списки (коллекции)
    comments: list[OrderCommentResponse] = []
    payments: list[PaymentResponse] = []
    parts: list[OrderPartResponse] = []
    works: list[WorkResponse] = []

    # Дополнительные вычисляемые поля
    calculated_price: float = 0
    allowed_statuses: list[str] = []


@dataclass(frozen=True, slots=True)
class ReadOrderCommand:
    uuid: UUID


class ReadOrderCommandHandler:
    def __init__(
        self,
        order_reader: OrderReader,
        order_service: OrderService,
    ) -> None:
        self._order_reader = order_reader
        self._order_service = order_service

    async def run(self, data: ReadOrderCommand, current_employee: Employee) -> ReadOrderOneResponse:
        order = await ensure_exists(
            self._order_reader.read_by_uuid, OrderUUID(data.uuid),
            f"Order with uuid {data.uuid}",
        )

        response = ReadOrderOneResponse.model_validate(order)

        # 1) Итоговая цена заказа
        response.calculated_price = self._order_service.calculate_total_price(order)

        # 2) Доступные статусы для текущего пользователя
        allowed_statuses: list[OrderStatus] = self._order_service.allowed_statuses_for_position(
            current_employee.position,
        )
        response.allowed_statuses = [s.value for s in allowed_statuses]

        return response
