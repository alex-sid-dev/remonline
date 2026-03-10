from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import structlog
from pydantic import BaseModel, ConfigDict

from src.application.ports.payment_reader import PaymentReader
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_payment").bind(service="payment")


@dataclass(frozen=True, slots=True)
class ReadAllPaymentCommand:
    pass


class ReadPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    order_id: int
    amount: float
    payment_method: str
    employee_id: int | None = None
    comment: str | None = None
    created_at: datetime | None = None


class ReadAllPaymentCommandHandler:
    def __init__(
        self,
        payment_reader: PaymentReader,
    ) -> None:
        self._payment_reader = payment_reader

    async def run(
        self,
        data: ReadAllPaymentCommand,
        current_employee: Employee,
    ) -> list[ReadPaymentResponse]:
        payments = await self._payment_reader.read_all(
            organization_id=current_employee.organization_id,
        )
        return [ReadPaymentResponse.model_validate(p) for p in payments]
