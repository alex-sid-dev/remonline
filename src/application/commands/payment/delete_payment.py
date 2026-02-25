from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists
from src.application.ports.payment_reader import PaymentReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee
from src.entities.payments.models import PaymentUUID

logger = structlog.get_logger("delete_payment").bind(service="payment")


@dataclass(frozen=True, slots=True)
class DeletePaymentCommand:
    uuid: UUID


class DeletePaymentCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        payment_reader: PaymentReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._payment_reader = payment_reader

    async def run(self, data: DeletePaymentCommand, current_employee: Employee) -> None:
        payment = await ensure_exists(
            self._payment_reader.read_by_uuid,
            PaymentUUID(data.uuid),
            f"Payment with uuid {data.uuid}",
        )

        await self._entity_saver.delete(payment)
        await self._transaction.commit()
        logger.info("Payment deleted successfully", payment_uuid=str(data.uuid))
