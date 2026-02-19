from dataclasses import dataclass
from typing import Optional
from uuid import UUID
import structlog

from src.application.commands.base_command_handler import BaseCommandHandler
from src.application.ports.payment_reader import PaymentReader
from src.application.ports.order_reader import OrderReader
from src.application.ports.employee_reader import EmployeeReader
from src.application.ports.transaction import Transaction, EntitySaver
from src.entities.payments.services import PaymentService
from src.entities.employees.models import Employee, EmployeeUUID
from src.entities.orders.models import OrderUUID
from src.application.errors._base import EntityNotFoundError

logger = structlog.get_logger("create_payment").bind(service="payment")


@dataclass
class CreatePaymentCommandResponse:
    uuid: UUID


@dataclass
class CreatePaymentCommand:
    order_uuid: UUID
    amount: float
    payment_method: str
    employee_uuid: Optional[UUID] = None
    comment: Optional[str] = None


class CreatePaymentCommandHandler(BaseCommandHandler):
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
        order = await self._order_reader.read_by_uuid(OrderUUID(data.order_uuid))
        if not order:
            raise EntityNotFoundError(message=f"Order with uuid {data.order_uuid} not found")

        employee_id = None
        if data.employee_uuid:
            employee = await self._employee_reader.read_by_uuid(EmployeeUUID(data.employee_uuid))
            if not employee:
                raise EntityNotFoundError(message=f"Employee with uuid {data.employee_uuid} not found")
            employee_id = employee.id

        payment = self._payment_service.create_payment(
            order_id=order.id,
            amount=data.amount,
            payment_method=data.payment_method,
            employee_id=employee_id,
            comment=data.comment
        )
        self._entity_saver.add_one(payment)
        await self._transaction.commit()
        logger.info("Payment created successfully", payment_uuid=str(payment.uuid))
        return CreatePaymentCommandResponse(
            uuid=payment.uuid,
        )
