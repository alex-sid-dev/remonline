from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.commands.payment.read_all_payment import ReadPaymentResponse
from src.application.errors._base import EntityNotFoundError
from src.application.ports.payment_reader import PaymentReader
from src.entities.employees.models import Employee
from src.entities.payments.models import PaymentUUID

logger = structlog.get_logger("read_payment").bind(service="payment")


@dataclass
class ReadPaymentCommand:
    uuid: UUID


class ReadPaymentCommandHandler(BaseCommandHandler):
    def __init__(
        self,
        payment_reader: PaymentReader,
    ) -> None:
        self._payment_reader = payment_reader

    async def run(
        self, data: ReadPaymentCommand, current_employee: Employee
    ) -> ReadPaymentResponse:
        payment = await self._payment_reader.read_by_uuid(PaymentUUID(data.uuid))
        if not payment:
            raise EntityNotFoundError(f"Payment with uuid {data.uuid} not found")

        return ReadPaymentResponse.from_entity(payment)
