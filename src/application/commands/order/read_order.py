from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
import structlog
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.entities.orders.models import OrderUUID
from src.entities.orders.services import OrderService
from src.entities.orders.enum import OrderStatus
from src.entities.employees.models import Employee
from src.application.commands.order.read_all_order import ReadOrderResponse
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("read_order").bind(service="order")


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Позволяет работать с объектами SQLAlchemy


class ClientShortResponse(BaseResponse):
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None


class DeviceShortResponse(BaseResponse):
    model: str
    brand: Optional[str] = None
    serial_number: Optional[str] = None

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
    creator: Optional[EmployeeShortResponse] = None  # кто оставил комментарий


class PaymentResponse(BaseResponse):
    uuid: UUID
    amount: float
    payment_method: str
    created_at: datetime

class PartShortResponse(BaseResponse):
    uuid: UUID
    name: str
    sku: Optional[str] = None
    price: Optional[float] = None

class OrderPartResponse(BaseResponse):
    uuid: UUID
    part_id: int
    qty: int
    price: Optional[float] = None
    part_info: Optional[PartShortResponse] = None # Если добавите маппинг выше


class WorkResponse(BaseResponse):
    uuid: UUID
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    qty: int = 1
    employee: Optional[EmployeeShortResponse] = None  # Кто выполнял работу


# --- Основная схема ответа ---

class ReadOrderOneResponse(BaseResponse):
    id: int
    uuid: UUID
    status: str
    problem_description: Optional[str] = None
    comment: Optional[str] = None
    price: Optional[float] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Вложенные сущности (автоподгруженные)
    client: ClientShortResponse
    device: DeviceShortResponse
    creator: Optional[EmployeeShortResponse] = None
    assigned_employee: Optional[EmployeeShortResponse] = None

    # Списки (коллекции)
    comments: List[OrderCommentResponse] = []
    payments: List[PaymentResponse] = []
    parts: List[OrderPartResponse] = []
    works: List[WorkResponse] = []

    # Дополнительные вычисляемые поля
    calculated_price: float = 0
    allowed_statuses: List[str] = []


@dataclass
class ReadOrderCommand:
    uuid: UUID


class ReadOrderCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            order_reader: OrderReader,
            order_service: OrderService,
    ) -> None:
        self._order_reader = order_reader
        self._order_service = order_service

    async def run(self, data: ReadOrderCommand, current_employee: Employee) -> ReadOrderOneResponse:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.uuid))
        if not order:
            raise EntityNotFoundError(message=f"Order with uuid {data.uuid} not found")

        response = ReadOrderOneResponse.model_validate(order)

        # 1) Итоговая цена заказа
        response.calculated_price = self._order_service.calculate_total_price(order)

        # 2) Доступные статусы для текущего пользователя
        allowed_statuses: List[OrderStatus] = self._order_service.allowed_statuses_for_position(
            current_employee.position,
        )
        response.allowed_statuses = [s.value for s in allowed_statuses]

        return response
