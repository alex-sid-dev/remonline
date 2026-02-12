from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.payment_reader import PaymentReader
from src.application.ports.transaction import Transaction
from src.entities.payments.models import PaymentUUID
from src.entities.payments.services import PaymentService
from src.entities.employees.models import Employee, EmployeeID
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("update_payment").bind(service="payment")

@dataclass
class UpdatePaymentCommand:
    uuid: UUID
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    comment: Optional[str] = None
    employee_id: Optional[int] = None

class UpdatePaymentCommandHandler(BaseCommandHandler):
    def __init__(
            self,
            transaction: Transaction,
            payment_reader: PaymentReader,
            payment_service: PaymentService,
    ) -> None:
        self._transaction = transaction
        self._payment_reader = payment_reader
        self._payment_service = payment_service

    async def run(self, data: UpdatePaymentCommand, current_employee: Employee) -> None:
        payment = await self._payment_reader.read_by_uuid(PaymentUUID(data.uuid))
        if not payment:
            raise EntityNotFoundError(f"Payment with uuid {data.uuid} not found")

        self._payment_service.update_payment(
            payment=payment,
            amount=data.amount,
            payment_method=data.payment_method,
            comment=data.comment,
            employee_id=EmployeeID(data.employee_id) if data.employee_id is not None else None
        )
        await self._transaction.commit()
        logger.info("Payment updated successfully", payment_uuid=str(data.uuid))
