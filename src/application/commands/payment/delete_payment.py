from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.errors._base import EntityNotFoundError
from src.application.ports.payment_reader import PaymentReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.employees.models import Employee
from src.entities.payments.models import PaymentUUID

logger = structlog.get_logger("delete_payment").bind(service="payment")


@dataclass
class DeletePaymentCommand:
    uuid: UUID


class DeletePaymentCommandHandler(BaseCommandHandler):
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
        payment = await self._payment_reader.read_by_uuid(PaymentUUID(data.uuid))
        if not payment:
            raise EntityNotFoundError(f"Payment with uuid {data.uuid} not found")

        await self._entity_saver.delete(payment)
        await self._transaction.commit()
        logger.info("Payment deleted successfully", payment_uuid=str(data.uuid))
