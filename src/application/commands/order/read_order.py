from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID
import structlog
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.order_reader import OrderReader
from src.entities.orders.models import OrderUUID
from src.entities.employees.models import Employee
from src.application.commands.order.read_all_order import ReadOrderResponse
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("read_order").bind(service="order")


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Позволяет работать с объектами SQLAlchemy


class ClientShortResponse(BaseResponse):
    id: int
    full_name: str
    phone: Optional[str] = None


class DeviceShortResponse(BaseResponse):
    id: int
    model: str
    brand: Optional[str] = None
    serial_number: Optional[str] = None


class EmployeeShortResponse(BaseResponse):
    id: int
    full_name: str


class OrderCommentResponse(BaseResponse):
    id: int
    text: str = Field(validation_alias=AliasChoices("comment", "text"))  # ORM has .comment
    created_at: datetime
    creator: Optional[EmployeeShortResponse] = None  # кто оставил комментарий


class PaymentResponse(BaseResponse):
    id: int
    uuid: UUID
    amount: float
    payment_method: str
    created_at: datetime

class PartShortResponse(BaseResponse):
    id: int
    uuid: UUID
    name: str
    sku: Optional[str] = None
    price: Optional[float] = None

class OrderPartResponse(BaseResponse):
    id: int
    uuid: UUID
    part_id: int
    qty: int
    price: Optional[float] = None
    part_info: Optional[PartShortResponse] = None # Если добавите маппинг выше


class WorkResponse(BaseResponse):
    id: int
    uuid: UUID
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
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


@dataclass
class ReadOrderCommand:
    uuid: UUID


class ReadOrderCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            order_reader: OrderReader,
    ) -> None:
        self._order_reader = order_reader

    async def run(self, data: ReadOrderCommand, current_employee: Employee) -> ReadOrderOneResponse:
        order = await self._order_reader.read_by_uuid(OrderUUID(data.uuid))
        if not order:
            raise EntityNotFoundError(message=f"Order with uuid {data.uuid} not found")

        return ReadOrderOneResponse.model_validate(order)
