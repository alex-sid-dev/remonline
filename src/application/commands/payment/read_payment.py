from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.commands.payment.read_all_payment import ReadPaymentResponse
from src.application.ports.payment_reader import PaymentReader
from src.entities.employees.models import Employee
from src.entities.payments.models import PaymentUUID

logger = structlog.get_logger("read_payment").bind(service="payment")


@dataclass(frozen=True, slots=True)
class ReadPaymentCommand:
    uuid: UUID


class ReadPaymentCommandHandler:
    def __init__(
        self,
        payment_reader: PaymentReader,
    ) -> None:
        self._payment_reader = payment_reader

    async def run(
        self, data: ReadPaymentCommand, current_employee: Employee
    ) -> ReadPaymentResponse:
        payment = await ensure_exists(
            self._payment_reader.read_by_uuid, PaymentUUID(data.uuid),
            f"Payment with uuid {data.uuid}",
        )
        return ReadPaymentResponse.model_validate(payment)
