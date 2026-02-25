from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.ports.payment_reader import PaymentReader
from src.application.ports.transaction import Transaction
from src.entities.employees.models import Employee, EmployeeID
from src.entities.payments.models import PaymentUUID
from src.entities.payments.services import PaymentService

logger = structlog.get_logger("update_payment").bind(service="payment")


@dataclass(frozen=True, slots=True)
class UpdatePaymentCommand:
    uuid: UUID
    amount: float | None = None
    payment_method: str | None = None
    comment: str | None = None
    employee_id: int | None = None


class UpdatePaymentCommandHandler:
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
        payment = await ensure_exists(
            self._payment_reader.read_by_uuid,
            PaymentUUID(data.uuid),
            f"Payment with uuid {data.uuid}",
        )

        self._payment_service.update_payment(
            payment=payment,
            amount=data.amount,
            payment_method=data.payment_method,
            comment=data.comment,
            employee_id=EmployeeID(data.employee_id) if data.employee_id is not None else None,
        )
        await self._transaction.commit()
        logger.info("Payment updated successfully", payment_uuid=str(data.uuid))
