from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.payment_reader import PaymentReader
from src.entities.payments.models import Payment
from src.entities.employees.models import Employee

logger = structlog.get_logger("read_all_payment").bind(service="payment")

@dataclass
class ReadAllPaymentCommand:
    pass

@dataclass
class ReadPaymentResponse:
    id: int
    uuid: str
    order_id: int
    amount: float
    payment_method: str
    employee_id: Optional[int]
    comment: Optional[str]
    created_at: Optional[datetime]

    @classmethod
    def from_entity(cls, entity: Payment) -> "ReadPaymentResponse":
        return cls(
            id=entity.id,
            uuid=str(entity.uuid),
            order_id=entity.order_id,
            amount=entity.amount,
            payment_method=entity.payment_method,
            employee_id=entity.employee_id,
            comment=entity.comment,
            created_at=entity.created_at
        )

class ReadAllPaymentCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            payment_reader: PaymentReader,
    ) -> None:
        self._payment_reader = payment_reader

    async def run(self, data: ReadAllPaymentCommand, current_employee: Employee) -> List[ReadPaymentResponse]:
        payments = await self._payment_reader.read_all()
        return [ReadPaymentResponse.from_entity(p) for p in payments]
