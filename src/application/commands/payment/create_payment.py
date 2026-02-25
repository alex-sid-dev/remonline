from dataclasses import dataclass
from uuid import UUID

import structlog

from src.application.commands._helpers import ensure_exists, resolve_employee_id
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.payment_reader import PaymentReader
from src.application.ports.transaction import EntitySaver, Transaction
from src.entities.orders.models import OrderUUID
from src.entities.payments.services import PaymentService

logger = structlog.get_logger("create_payment").bind(service="payment")


@dataclass(frozen=True, slots=True)
class CreatePaymentCommandResponse:
    uuid: UUID


@dataclass(frozen=True, slots=True)
class CreatePaymentCommand:
    order_uuid: UUID
    amount: float
    payment_method: str
    employee_uuid: UUID | None = None
    comment: str | None = None


class CreatePaymentCommandHandler:
    def __init__(
        self,
        transaction: Transaction,
        entity_saver: EntitySaver,
        payment_service: PaymentService,
        payment_reader: PaymentReader,
        order_reader: OrderReader,
        employee_reader: EmployeeReader,
    ) -> None:
        self._transaction = transaction
        self._entity_saver = entity_saver
        self._payment_reader = payment_reader
        self._payment_service = payment_service
        self._order_reader = order_reader
        self._employee_reader = employee_reader

    async def run(self, data: CreatePaymentCommand) -> CreatePaymentCommandResponse:
        order = await ensure_exists(
            self._order_reader.read_by_uuid, OrderUUID(data.order_uuid),
            f"Order with uuid {data.order_uuid}",
        )

        employee_id = await resolve_employee_id(self._employee_reader, data.employee_uuid)

        payment = self._payment_service.create_payment(
            order_id=order.id,
            amount=data.amount,
            payment_method=data.payment_method,
            employee_id=employee_id,
            comment=data.comment,
        )
        self._entity_saver.add_one(payment)
        await self._transaction.commit()
        logger.info("Payment created successfully", payment_uuid=str(payment.uuid))
        return CreatePaymentCommandResponse(
            uuid=payment.uuid,
        )
